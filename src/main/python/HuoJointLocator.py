

import matplotlib
#matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from functools import partial
plt.ion()
import numpy as np
#from functions import affineWarp,affineWarpImage, fourierCurve, fourierFit, linearWarp, linearWarpImage, fourierCurve2, fourierFit2,fourierFit3
import os

import cv2
from skimage.filters.rank import entropy
from skimage.morphology import disk
from skimage.filters import threshold_otsu
from skimage.segmentation import flood, flood_fill
from scipy.signal import find_peaks
from scipy.interpolate import Rbf,CubicSpline
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
import scipy.ndimage as ndi
from extract_patches.core import extract_patches
import time
import tensorflow as tf
import tensorflow_addons as tfa

class initialize_shape_model(object):
    def __init__(self,image):
        self.image = image

    def __call__(self):

        pass



class huo_method(object):
    def __init__(self,image,nFingers=10,side = 'b',polynom_degree=2,PATCH_SIZE = 200,mrSize=1.0):
        self.nFingers = nFingers
        if nFingers ==10:
            self.nPhanlanges = 8
        elif nFingers ==5:
            self.nPhanlanges = 4
        self.whole_image    = image
        nX,nY = image.shape
        self.image    = image#[:,0:nY//2]
        self._debug_flag = False
        self._polynom_deg = polynom_degree
        self._patch_size = PATCH_SIZE
        self._mrSize  = mrSize
        #self.finger_lines = {}

    def extract_hand_mask_unet(self,_plot=False):
        """
        Uses u-net to get a hand mask fro the x-ray
        :param _plot:
        :return:
        """
        pass

    def extract_hand_mask(self,_plot=False):
        """
        uses entropy and otsu thresholding to create mask for hand location
        (i)   sum_i=0^n p(x_i)log_2 p(x_i) p normalised histogram value for bin x_i, n number of bins in hostogram of
        patch of area 9 \times 9
        (ii)  otsu threholding performed on entropy based image E
        (iii) flood filling in horizontal direction to get complete hand mask
        :return: numpy array same size as the image
        """
        print("==================================================================")
        print("Finding hand mask using otsu thresholding and flood filling")
        t1 = time.time()
        im = np.zeros(self.image.shape)
        im[100:-100,200:-200] = self.image[100:-100,200:-200]
        im =  im.astype(np.uint8)
        entropy_image = entropy(im,disk(9))
        thresh = threshold_otsu(entropy_image)
        bin_image = (entropy_image > thresh).astype(np.int)
        seed_points = np.where(bin_image == 1)

        flood_filled = flood_fill(bin_image,(seed_points[0][0],seed_points[1][0]),1,tolerance=1)
        binary_filled = ndi.binary_fill_holes(bin_image,structure=np.ones((5,5))).astype(int)

        # binary_pad = np.zeros(binary_filled.shape)
        # binary_pad[100:-100,200:-200] = binary_filled[100:-100,200:-200]
        if self._debug_flag:
            fig,(ax0,ax1,ax2,ax3) = plt.subplots(ncols=4,figsize=(24,4))

            img0 = ax0.imshow(im,cmap=plt.cm.gray)
            ax0.set_title("Image")
            ax0.axis("off")
            fig.colorbar(img0,ax=ax0)

            img1 = ax1.imshow(entropy_image,cmap='gray')
            ax1.set_title("Entropy-image")
            ax1.axis("off")
            fig.colorbar(img1,ax=ax1)

            img2 = ax2.imshow(bin_image,cmap='gray')
            ax2.set_title("Otsu-threshold")
            ax2.axis("off")
            fig.colorbar(img2,ax=ax2)

            img3 = ax3.imshow(binary_filled ,cmap='gray')
            ax3.set_title("binary-filled after thresholding")
            ax3.axis("off")
            fig.colorbar(img3,ax=ax3)
            fig.tight_layout()

            plt.show()


        self._bin_filled_image = binary_filled
        print("time taken = {:}".format(time.time()-t1))
        return binary_filled


    def get_finger_midlines_init(self,_plot=False):
        """
        acts on masked hand
        Performs Gaussian blurring to locate self.Nfingers corresponfing to the metacarpals, uses the peak of each
        blurred outline
        projected
        horizontally as a
        representing the midpoint of the fingers
        :return: numpy array [self.Nfingers,N,2] self.Nfingers peaks represented by N 2-d points
        """
        t1 = time.time()

        pixel_width = 0.1
        sigmas = np.arange(20,55,step=5) #todo: change this to reflect pizel sizes
        n_peaks = self.nFingers


        #recovered peaks is [xloc, yloc1, yloc2,...,ylocn_peaks] shape [n_hor,n_peaks+1]
        #where [xloc,yloci] is the i-th peak along the xloc
        final_peaks = np.ones(1)
        midl_len    = 0
        sliding_steps = np.arange(0,self.image.shape[0] - 100,10)
        k =0
        print("=================================================================")
        print("Finding finger midlines")
        for sigma in sigmas:
            print("gaussian filter with sigma ={:}".format(sigma))
            print("-----------------------------------------------------------------")
            t_gauss = time.time()
            gaussian_filt = ndi.gaussian_filter(self.image* self._bin_filled_image.astype(np.float),sigma=sigma)
            print("time taken to apply filter={:}".format(time.time() - t_gauss))
            if k==0:
                self._gaussian_fltrd_init = gaussian_filt
            t_peak = time.time()
            recovered_peaks = find_peaks_horizontal(gaussian_filt,n_peaks,startInd=0,endInd=self.image.shape[0]-100)
            print("time taken to find peak={:}".format(time.time()-t_peak))
            midl_len = recovered_peaks.shape[0]
                    #i += 1
            if midl_len > final_peaks.shape[0]:
                final_peaks = recovered_peaks
                self._gaussian_fltrd_init = gaussian_filt
            k+=1

        self._finger_midpoints_init = final_peaks
        if self._debug_flag:
            fig,axes = plt.subplots(nrows=2,figsize=(24,12))
            axes[0].imshow(self._gaussian_fltrd_init)
            for i in range(final_peaks.shape[0]):
                hor_cross = final_peaks[i,0]
                hor_arr = np.ones(self._gaussian_fltrd_init.shape[1]) * hor_cross
                ver_arr = np.arange(self._gaussian_fltrd_init.shape[1])

                peaks = final_peaks[i,1:]
                axes[0].plot(ver_arr,hor_arr)
                axes[1].plot(self._gaussian_fltrd_init[hor_cross,:])
                for peak in peaks:
                    axes[1].plot(peak,self._gaussian_fltrd_init[hor_cross,peak],'o')
            plt.figure()
            plt.imshow(self.image)
            for i in range(n_peaks):
                plt.plot(final_peaks[:,i + 1],final_peaks[:,0],'w')
            plt.show()

        end_ind = np.min(self._finger_midpoints_init[:,0])
        pixel_width = 0.1
        sigmas = np.arange(20,55,step=5)#todo: make this reflect pixel sizes

        n_peaks = self.nPhanlanges

        final_peaks = np.ones(1)
        midl_len    = 0
        sliding_steps = np.arange(0,end_ind,10)

        k =0
        for sigma in sigmas:
            t_gauss = time.time()
            gaussian_filt = ndi.gaussian_filter(self.image* self._bin_filled_image.astype(np.float),sigma=sigma)
            print("time taken to apply filter={:}".format(time.time() - t_gauss))
            if k==0:
                self._gaussian_fltrd = gaussian_filt
            t11 = time.time()

            recovered_peaks = find_peaks_horizontal(gaussian_filt,n_peaks,startInd=0,endInd=end_ind)
            print("time taken to find peak={:}".format(time.time() - t11))
            midl_len = recovered_peaks.shape[0]
                    #i += 1
            if midl_len > final_peaks.shape[0]:
                final_peaks = recovered_peaks
                self._gaussian_fltrd = gaussian_filt
            k+=1
        print("time taken = {:}".format(time.time() - t1))
        self._finger_midpoints = final_peaks

        ndiscr = self._finger_midpoints_init.shape[1]



        if self._debug_flag:
            fig,axes = plt.subplots(nrows=2,figsize=(24,12))

            axes[0].imshow(self._gaussian_fltrd)
            for i in range(final_peaks.shape[0]):
                hor_cross = final_peaks[i,0]
                hor_arr = np.ones(self._gaussian_fltrd.shape[1]) * hor_cross
                ver_arr = np.arange(self._gaussian_fltrd.shape[1])

                peaks = final_peaks[i,1:]
                axes[0].plot(ver_arr,hor_arr)
                axes[1].plot(self._gaussian_fltrd[hor_cross,:])
                for peak in peaks:
                    axes[1].plot(peak,self._gaussian_fltrd[hor_cross,peak],'o')
            plt.figure()
            plt.imshow(self.image)
            for i in range(n_peaks):
                plt.plot(final_peaks[:,i + 1],final_peaks[:,0],'w')
            plt.show()


    def _extend_upwards(self,_plot=True):
        """
        uses self._finger_midpoints_init and self._finger_midpoints to built a smoothing function which provides a
        direction to look for peaks in the gaussian filtered image
        initializes self._phalanges and self._thumbs as spline lists storing the midlines of phalanges and thumbs
        respectively
        has a tolerance to refit the smoothing function
        :param _plot:
        :return:
        """
        #this is to extend upwards for all fingers
        tol    = 5
        degree = self._polynom_deg
        x_init = self._finger_midpoints_init[:,0]
        x_new  = self._finger_midpoints[:,0]
        y_init = np.concatenate((self._finger_midpoints_init[:,1:5],self._finger_midpoints_init[:,7:]),axis=1)
        y_new  = self._finger_midpoints[:,1:]

        X       = np.concatenate((x_new,x_init))
        end_ind = np.min(X)
        Y       = np.concatenate((y_new,y_init),axis=0)
        nThin   = 1

        sliding_steps = np.arange(0,end_ind,5)

        gaussian_filt = self._gaussian_fltrd*self._bin_filled_image  #ndi.gaussian_filter(im,sigma=sigma)*bin_mask.astype(np.float)
        if self.nFingers==10:
            self._thumbs = [CubicSpline(x_init,self._finger_midpoints_init[:,5]),
                            CubicSpline(x_init,self._finger_midpoints_init[:,6])]
        elif self.nFingers==5:
            self._thumbs = [CubicSpline(x_init,self._finger_midpoints_init[:,5])]

        pixel_width = 0.1
        sigmas      = np.arange(20,55,step=5)

        if self._debug_flag:
            fig,ax = plt.subplots(ncols=2,figsize=(12,32))

            ax[0].imshow(self.image,cmap  ='Greys_r')
            ax[0].plot(y_new,x_new,label  ='upward extension detecting 8 peaks',color='w')
            ax[0].plot(y_init,x_init,label='initial extension detetction 10 peaks',color='limegreen')
            ax[1].imshow(self.image,cmap  ='Greys_r')
        self._phalanges = []
        for k in range(Y.shape[1]):
            x = X.copy()
            y = Y[:,k]

            model = make_pipeline(PolynomialFeatures(degree),Ridge())
            model.fit(np.expand_dims(x[::nThin],axis=1),y[::nThin])
            predictions = model.predict(np.expand_dims(sliding_steps[::-1],axis=1))

            if self._debug_flag:
                ax[0].plot(predictions,sliding_steps,label='cubic spline prediction')

            i = 0

            peaks_final = np.array([])
            x_locs      = np.array([])
            for hor_cross in sliding_steps[::-1]:
                signal  = gaussian_filt[hor_cross,:]
                peaks   = find_peaks(signal,height=None,threshold=None,distance=None,prominence=[5],width=None,
                                     wlen=None,
                                   rel_height=0.5,plateau_size=None)
                pred_y = predictions[i]

                #choose which peak is closest to the interpolated value
                if len(peaks[0]) > 0:
                    distances = np.abs(peaks[0] - pred_y)
                    ind       = np.where(distances < 10)

                    if len(ind[0]) == 1:

                        peak        = peaks[0].ravel()[ind]
                        peaks_final = np.append(peaks_final,peak)
                        x_locs      = np.append(x_locs,hor_cross)

                        #check how the line is doing: by looking at total deviation, if too much, refit cubicspline
                        if np.linalg.norm(peaks_final - model.predict(np.expand_dims(x_locs,axis=1)) )/ (i + 1) > tol:
                            #print('fixing the line')

                            x = np.concatenate((x[::-1],sliding_steps[::-1][i:i + 1]))
                            y = np.concatenate((y[::-1],peaks_final[i:i + 1].astype(np.float)))
                            model = make_pipeline(PolynomialFeatures(degree),Ridge())
                            model.fit(np.expand_dims(x[::nThin],axis=1),y[::nThin])
                            #y_plot = model.predict(X_plot)
                            predictions = model.predict(np.expand_dims(sliding_steps[::-1],axis=1))

                            #cs          = CubicSpline(x[::nThin], y[::nThin])
                            #predictions = cs(sliding_steps[i:])
                i += 1

            x_final = np.concatenate((X,x_locs))

            y_final = np.concatenate((Y[:,k],peaks_final))
            arg_sort = np.argsort(x_final)
            self._phalanges = self._phalanges + [CubicSpline(x_final[arg_sort],y_final[arg_sort]
                                                             )]

            if self._debug_flag:
                arg_sort = np.argsort(x)
                ax[1].plot(y[arg_sort],x[arg_sort])
                ax[1].plot(peaks_final,x_locs)


    def plot_fingers(self):
        plt.figure()
        plt.imshow(self.image)
        for cs in self._phalanges+self._thumbs:
            plt.plot(cs(cs.x),cs.x,color='b')



    def _extend_downwards(self,_plot=False):
        """
        uses self._phalanges and self._thumbs to built a smoothing function which provides a
        direction to look for peaks below the current finger midlines in the gaussian filtered image
        overwrites self._phalanges and self._thumbs as spline lists storing the midlines of phalanges and thumbs
        respectively
        has a tolerance to refit the smoothing function
        :param _plot:
        :return:
        """
        #this is to extend downwards for all fingers
        tol         = 5
        degree      = self._polynom_deg
        pixel_width = 0.1
        sigmas      = np.arange(20,55,step=5)
        nThin       = 1
        if self._debug_flag:
            fig,ax = plt.subplots(ncols=2,figsize=(12,24))
        gaussian_filt = self._gaussian_fltrd*self._bin_filled_image
        niter = 0
        for cs in self._phalanges+self._thumbs:
            x = cs.x
            y = cs(cs.x)
            start_ind     = np.max(x)+10
            end_ind       = self.image.shape[0]-300
            sliding_steps = np.arange(start_ind,end_ind,10).astype(np.int)
            model = make_pipeline(PolynomialFeatures(degree),Ridge())
            model.fit(np.expand_dims(x[::nThin],axis=1),y[::nThin])
            predictions = model.predict(np.expand_dims(sliding_steps,axis=1))

            i = 0
            peaks_final = np.array([])
            x_locs      = np.array([])
            for hor_cross in sliding_steps:

                signal  = gaussian_filt[hor_cross,:]
                peaks   = find_peaks(signal,height=None,threshold=None,distance=None,prominence=[1],width=None,
                                     wlen=None,
                                   rel_height=0.5,plateau_size=None)
                pred_y = predictions[i]

                #choose which peak is closest to the interpolated value
                if len(peaks[0]) > 0:
                    distances = np.abs(peaks[0] - pred_y)
                    ind       = np.where(distances < 10)

                    if len(ind[0]) == 1:

                        peak        = peaks[0].ravel()[ind]
                        peaks_final = np.append(peaks_final,peak)
                        x_locs      = np.append(x_locs,hor_cross)

                        #check how the line is doing: by looking at total deviation, if too much, refit cubicspline
                        if np.linalg.norm(peaks_final - model.predict(np.expand_dims(x_locs,axis=1)) )/ (i + 1) > tol:
                            #print('fixing the line')
                            x = np.concatenate((x,sliding_steps[i:i + 1]))
                            y = np.concatenate((y,peaks_final[i:i + 1].astype(np.float)))
                            model = make_pipeline(PolynomialFeatures(degree),Ridge())
                            model.fit(np.expand_dims(x[::nThin],axis=1),y[::nThin])

                            predictions = model.predict(np.expand_dims(sliding_steps,axis=1))
                i += 1

            x_final = np.concatenate((cs.x,x_locs))
            y_final = np.concatenate((cs(cs.x),peaks_final))
            arg_sort = np.argsort(x_final)


            if niter<self.nPhanlanges:
                self._phalanges[niter] = CubicSpline(x_final[arg_sort],y_final[arg_sort])
            elif niter==5:
                self._thumbs[0] = CubicSpline(x_final[arg_sort],y_final[arg_sort])
            elif niter==6:
                self._thumbs[1] = CubicSpline(x_final[arg_sort],y_final[arg_sort])

            niter+=1
            if self._debug_flag:

                ax[0].imshow(self.image,cmap='Greys_r')
                ax[0].plot(cs(cs.x),cs.x,color='b')
                ax[0].plot(predictions,sliding_steps)
                arg_sort = np.argsort(x)
                ax[1].imshow(self.image,cmap='Greys_r')
                ax[1].plot(y[arg_sort],x[arg_sort],color='b')
                ax[1].plot(peaks_final,x_locs,color='limegreen')


    def get_finger_midlines(self,_plot=False):
        self.get_finger_midlines_init(_plot=_plot)
        self._extend_upwards(_plot=_plot)
        self._extend_downwards(_plot=_plot)

    def _get_directional_fields(self):
        """
        uses the splines fit to generate a tangent field that will be used in the extraction of the joint features.
        The tangent fields will be dot producted with the 1st and 2nd order image derivatives imformation
        :return:
        """
        pass



    def _generate_mask_from_curve(self,cs,_plot=False):
        X = np.expand_dims(cs.x,1)
        y = cs(cs.x)
        degree = self._polynom_deg
        model = make_pipeline(PolynomialFeatures(degree),Ridge())
        model.fit(X,y)

        y_sm = model.predict(X)
        mask = np.zeros(self.image.shape)
        pts_init = np.transpose(np.array([y_sm.astype(np.int),cs.x.astype(np.int)]))
        pts = pts_init.reshape((-1,1,2))
        isClosed = False
        # color in BGR
        color = (255,255,255)
        # Line thickness of 8 px
        thickness = 8
        mask = cv2.polylines(mask,[pts],
                             isClosed,color,
                             thickness)
        kernel = np.ones((5,5),np.uint8)
        mask_dil = cv2.dilate(mask,kernel,iterations=30)
        mask_blurred = ndi.gaussian_filter(mask_dil,sigma=20)
        if _plot:
            fig,ax = plt.subplots(ncols =3 )
            ax[0].imshow(mask,cmap='Greys_r')
            ax[0].set_title('mask')
            ax[1].imshow(mask_blurred,cmap='Greys_r')
            ax[1].set_title('blurred mask')
            ax[2].imshow(mask_blurred*self.image,cmap='Greys_r')
            ax[2].set_title('blurre dmask applied to image')
            plt.axis('off')
            plt.tight_layout()
        return mask_blurred,model

    def _extract_joint_feature(self,cs,_plot=False,ksize=23):
        mask_blurred,model = self._generate_mask_from_curve(cs)
        im_blur = self.image  #*mask_blurred

        #1st,2nd order sobel gradients
        minx = np.int(np.min(cs.x))-50
        maxx = np.int(np.max(cs.x))+50
        miny = np.int(np.min(cs(cs.x)))-50
        maxy = np.int(np.max(cs(cs.x)))+50
        print("------------------------------------------------------")
        print("applying sobel features")
        sobelx = cv2.Sobel(im_blur,cv2.CV_32F,1,0,ksize=ksize)
        sobelxx = cv2.Sobel(sobelx,cv2.CV_32F,1,0,ksize=ksize)
        sobelxy = cv2.Sobel(sobelx,cv2.CV_32F,0,1,ksize=ksize)
        sobely = cv2.Sobel(im_blur,cv2.CV_32F,0,1,ksize=ksize)


        sobelyy = cv2.Sobel(sobelx,cv2.CV_32F,0,1,ksize=ksize)
        sobelyx = cv2.Sobel(sobelx,cv2.CV_32F,1,0,ksize=ksize)

        coeffs = model[1].coef_
        #1st,2nd order order gradients
        dirx,diry = np.gradient(im_blur)
        dirxx,dirxy = np.gradient(dirx)
        diryy,diryx = np.gradient(diry)


        search_dir = search_direction(np.arange(0,im_blur.shape[0]),coeffs)
        x_grad_arr = np.repeat(search_dir[:,0:1],axis=1,repeats=im_blur.shape[1])
        y_grad_arr = np.repeat(search_dir[:,1:2],axis=1,repeats=im_blur.shape[1])

        #directional derivatives
        directional_deriv = dirx * y_grad_arr + diry * x_grad_arr
        directional_deriv2 = dirxx * y_grad_arr ** 2 + 2 * dirxx * y_grad_arr * x_grad_arr + diryy * x_grad_arr ** 2

        directional_sobel = sobely * y_grad_arr + sobelx * x_grad_arr

        directional_sobel2 = sobelxx * x_grad_arr ** 2 + 2 * sobelxy * y_grad_arr * x_grad_arr + sobelyy * y_grad_arr\
                             ** 2

        s1 = 1.0
        s2 = 1.0
        g1 = 3.0
        g2 = 1.0
        if _plot: fig,ax = plt.subplots(ncols=5,figsize=(10,30))
        weighted_features = np.zeros(directional_deriv.shape)
        i = 0
        titles = ['1st order sobel','2nd order soberl','1st order derv','2nd order deriv']
        for weight,Im in zip([s1,s2,g1,g2],[directional_sobel,directional_sobel2,directional_deriv,directional_deriv2]):
            #Im = (Im-np.min(Im))/(np.max(Im)-np.min(Im))
            Im = Im / np.max(Im)

            weighted_features += weight * np.abs(Im) * mask_blurred

            if _plot:
                alpha = 1.0
                beta = 0.0
                #enhanced_features = directional_deriv2*alpha + beta
                enhanced_features = (Im) * alpha * mask_blurred + beta
                ax[i].imshow(enhanced_features[minx:maxx,miny:maxy],cmap='Greys')
                ax[i].set_title(titles[i])

                ax[i].axes.xaxis.set_visible(False)
                ax[i].axes.yaxis.set_visible(False)

            i += 1
        if _plot:
            alpha = 255
            beta = 0.0
            #enhanced_features = directional_deriv2*alpha + beta
            enhanced_features = weighted_features * alpha + beta
            ax[4].imshow(enhanced_features[minx:maxx,miny:maxy],cmap='Greys')
            ax[4].set_title('weighted gradient ')
            ax[4].axes.yaxis.set_visible(False)
            ax[4].axes.xaxis.set_visible(False)

        return directional_deriv2*mask_blurred

    def extract_joint_feature(self,_plot=False):
        """
        uses fingert midlines
        Directional LoG along each peak gives a responce for each joint. Strong positive response to dark joint
        space, strong negative response for bright cortical bone and edges. Absolute value of LoG is carried out to
        further increase blob response
        :return:
        """

        self._phalanges_features = []
        print("==================================================")
        for cs in self._phalanges:
            print("finding phalange features")
            t1 = time.time()
            out = self._extract_joint_feature(cs,_plot=_plot)
            self._phalanges_features = self._phalanges_features+[out]
            print("time taken = {:}".format(time.time() - t1))

        self._thumbs_features = []
        print("==================================================")
        for cs in self._thumbs:
            print("finding thumb features")
            t1 = time.time()
            out = self._extract_joint_feature(cs,_plot=_plot)
            self._thumbs_features = self._thumbs_features + [out]
            print("time taken = {:}".format(time.time() - t1))



    def locate_joints(self,_plot=False):
        """
        10*5 mm rectabgle traverses along the midline. For each point, sum of abs value of LoG within the rectrangle
        is calculated. use prior knowledge on bone length to get the actual location of joints.
        :return: tbd
        """
        joint_patch_library = {}
        joint_loc_library   = {}
        joint_types         = ['DIP','PIP','MCP']
        if _plot: fig,ax = plt.subplots(nrows=10,ncols = 3)
        k = 0
        print("locating patches")
        for phalanx,features in zip(self._phalanges,self._phalanges_features):
            if k/4 <1:
                side_name   = 'L'
                finger_name = str(5-k)
            else:
                side_name   = 'R'
                finger_name = str(k-2)



            mask,model = self._generate_mask_from_curve(phalanx)

            kern_height = int(10 / 0.11)
            kern_width = int(5 / 0.11)
            kernel = np.ones((kern_width,kern_height))

            # feature_trans = np.exp(-features**2/np.var(features))

            abs_features = np.abs(features)

            joint_blob = cv2.filter2D(abs_features,-1,kernel)
        # phalanx = [0]
            joint_blob_vals_spline = ndi.interpolation.map_coordinates(joint_blob,[phalanx.x,phalanx(phalanx.x)],
                                                                       order=1)


            mask,model = huo._generate_mask_from_curve(phalanx)

            X = np.expand_dims(phalanx.x,1)
            Y = model.predict(X)

            joint_blob_vals_smooth = ndi.interpolation.map_coordinates(joint_blob,[phalanx.x,Y],order=1)

            peaks = find_peaks(joint_blob_vals_smooth,height=None,threshold=None,distance=None,prominence=[1],width=None,
                           wlen=None,
                           rel_height=0.7,plateau_size=None)
            # print(peaks)
            prom_idx = sorted(np.argsort(peaks[1]['prominences'])[-3:])
            peak_idx = peaks[0][prom_idx]
            x_locs = phalanx.x[peak_idx]

            y_locs = phalanx(x_locs)

            Size = 120
            keypoints = [cv2.KeyPoint(y_locs[0],x_locs[0],120)]
            for i in [1]:
                keypoints = keypoints + [cv2.KeyPoint(y_locs[i],x_locs[i],120)]
            PATCH_SIZE = self._patch_size
            mrSize = self._mrSize
            patches = extract_patches(keypoints,im,PATCH_SIZE,mrSize,'cv2')
            keypoints = [cv2.KeyPoint(y_locs[2],x_locs[2],120)]
            patches = patches+ extract_patches(keypoints,im,PATCH_SIZE+20,mrSize,'cv2')
            for i in range(0,3):
                joint_name = joint_types[i]
                idx        = joint_name + '_' + finger_name + '_' + side_name
                joint_patch_library[idx] = patches[i]
                joint_loc_library[idx]   = np.array(x_locs[i],y_locs[i])

            if _plot:
                for i in range(0,3):
                    ax[k,i].imshow(patches[i])
            print(k)

            k += 1

        #todo: need to adjust method for thumbs
        # k = 0
        # joint_types = ['PIP','MCP']
        # for phalanx,features in zip(self._thumbs,self._thumbs_features):
        #     finger_name = str(1)
        #     if k==0 :
        #         side_name = 'L'
        #     else:
        #         side_name = 'R'
        #
        #
        #     mask,model = self._generate_mask_from_curve(phalanx)
        #
        #     kern_height = int(10 / 0.11)
        #     kern_width = int(5 / 0.11)
        #     kernel = np.ones((kern_width,kern_height))
        #
        #     # feature_trans = np.exp(-features**2/np.var(features))
        #
        #     abs_features = np.abs(features)
        #
        #     joint_blob = cv2.filter2D(abs_features,-1,kernel)
        #     # phalanx = [0]
        #     joint_blob_vals_spline = ndi.interpolation.map_coordinates(joint_blob,[phalanx.x,phalanx(phalanx.x)],
        #                                                                order=1)
        #
        #     mask,model = huo._generate_mask_from_curve(phalanx)
        #
        #     X = np.expand_dims(phalanx.x,1)
        #     Y = model.predict(X)
        #
        #     joint_blob_vals_smooth = ndi.interpolation.map_coordinates(joint_blob,[phalanx.x,Y],order=1)
        #
        #     peaks = find_peaks(joint_blob_vals_smooth,height=None,threshold=None,distance=None,prominence=[1],
        #                        width=None,
        #                        wlen=None,
        #                        rel_height=0.7,plateau_size=None)
        #     # print(peaks)
        #     prom_idx = sorted(np.argsort(peaks[1]['prominences'])[-3:])
        #     peak_idx = peaks[0][prom_idx]
        #     x_locs = phalanx.x[peak_idx]
        #
        #     y_locs = phalanx(x_locs)
        #
        #     Size = 120
        #     keypoints = [cv2.KeyPoint(y_locs[0],x_locs[0],120)]
        #     for i in [1]:
        #         keypoints = keypoints + [cv2.KeyPoint(y_locs[i],x_locs[i],120)]
        #     PATCH_SIZE = self._patch_size
        #     mrSize = self._mrSize
        #     patches = extract_patches(keypoints,im,PATCH_SIZE,mrSize,'cv2')
        #     keypoints = [cv2.KeyPoint(y_locs[2],x_locs[2],120)]
        #     patches = patches + extract_patches(keypoints,im,PATCH_SIZE + 20,mrSize,'cv2')
        #     for i in range(0,2):
        #         joint_name = joint_types[i]
        #         idx = joint_name + '_' + finger_name + '_' + side_name
        #         joint_patch_library[idx] = patches[i]
        #         joint_loc_library[idx] = np.array(x_locs[i],y_locs[i])
        #
        #     if _plot:
        #         for i in [0,1]:
        #             ax[k+8,i].imshow(patches[i])
        #     print(k)
        #
        #     k+=1

        self._joint_patch_library = joint_patch_library
        self._joint_loc_library   = joint_loc_library
        return joint_patch_library,joint_loc_library

    def __call__(self,_plot=False):
        t1 = time.time()
        self.extract_hand_mask(_plot=_plot)
        self.get_finger_midlines(_plot=_plot)
        self.extract_joint_feature(_plot=_plot)
        self.locate_joints()
        print("total time taken={:}".format(time.time()-t1))

def find_peaks_horizontal(gaussian_filt,n_peaks,startInd,endInd):
    sliding_steps = np.arange(startInd,endInd,10)
    i = 0
    recovered_peaks = np.array([[]])
    for hor_cross in sliding_steps:
        signal = gaussian_filt[hor_cross,:]
        peaks = find_peaks(signal,height=None,threshold=None,distance=None,prominence=[10],width=None,wlen=None,
                           rel_height=0.5,plateau_size=None)
        if peaks[0].shape[0] == n_peaks:
            if i == 0:
                recovered_peaks = np.expand_dims(np.append(hor_cross,np.sort(peaks[0])),axis=0)
            else:
                temp_peaks = np.expand_dims(np.append(hor_cross,np.sort(peaks[0])),axis=0)
                recovered_peaks = np.concatenate((recovered_peaks,temp_peaks),axis=0)

            i += 1
    return recovered_peaks


def search_direction(x,coeffs):
    """
    coeffs:=a0,a1,a2,...,an
    """

    dy = 0
    for d in range(len(coeffs) - 1):
        #print('coeff ={:2f}, x^d={:2f}'.format(coeffs[d+1],x**d))
        dy += (d + 1) * coeffs[d + 1] * x ** d
    dx = np.ones(x.shape)
    search_dir = np.transpose(np.array([-dy,dx]))
    return search_dir / np.linalg.norm(search_dir)


def test_joint_locator():
    """
    prototype for huo method joint extractor
    :return:
    :rtype:
    """
    features = huo._phalanges_features[0]
    mask, model = huo._generate_mask_from_curve(huo._phalanges[0])

    kern_height = int(10/0.11)
    kern_width  =  int(5/0.11)
    kernel      = np.ones((kern_height,kern_width))

    # feature_trans = np.exp(-features**2/np.var(features))

    abs_features = np.abs(features)

    joint_blob = cv2.filter2D(abs_features,-1,kernel)
    phalanx = huo._phalanges[0]
    joint_blob_vals_spline = ndi.interpolation.map_coordinates(joint_blob,[phalanx.x,phalanx(phalanx.x)],
                                                                                         order=1)
    fig,ax = plt.subplots(ncols=2)
    ax[0].imshow(joint_blob)
    ax[0].plot(phalanx(phalanx.x),phalanx.x)
    ax[0].set_title('Interpolcation of LoG done on 2-d spline locations')

    ax[1].plot(phalanx.x,joint_blob_vals_spline)
    ax[1].set_title('Values of LoG evaluated along spline')

    mask, model = huo._generate_mask_from_curve(phalanx)

    X = np.expand_dims(phalanx.x,1)
    Y = model.predict(X)

    joint_blob_vals_smooth = ndi.interpolation.map_coordinates(joint_blob,[phalanx.x,Y],order=1)
    fig,ax = plt.subplots(ncols=2)
    ax[0].imshow(joint_blob)
    ax[0].plot(Y,phalanx.x)
    ax[0].set_title('Interpolcation of LoG done on 2-d smoothed out spline')

    ax[1].plot(phalanx.x,joint_blob_vals_smooth)
    ax[1].set_title('Values of LoG evaluated along smoothed splinte')



    peaks   = find_peaks(joint_blob_vals_smooth,height=None,threshold=None,distance=None,prominence=[1],width=None,
                                         wlen=None,
                                       rel_height=0.7,plateau_size=None)
    prom_idx = sorted(np.argsort(peaks[1]['prominences'])[-3:])
    peak_idx = peaks[0][prom_idx]
    x_locs = phalanx.x[peak_idx]

    y_locs = phalanx(x_locs)

    from extract_patches.core import extract_patches

    Size = 120
    keypoints = [cv2.KeyPoint(y_locs[0],x_locs[0],120)]
    for i in [1,2]:
        keypoints = keypoints+[cv2.KeyPoint(y_locs[i],x_locs[i],120)]

    vis_img1 = None
    vis_img1 = cv2.drawKeypoints(im,keypoints,vis_img1,
                                 flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    plt.imshow(vis_img1)


    PATCH_SIZE = 200
    mrSize = 1.0
    patches = extract_patches(keypoints,im,PATCH_SIZE,mrSize,'cv2')

    show_idx = 0
    fig,ax = plt.subplots(ncols=3)
    for i in range(0,3):
        ax[i].imshow(patches[i])




if __name__=='__main__':
    # imLoc  = locations.LABELLED_XRAY_LOC_RAW
    imLoc = "/home/amr62/Documents/data/anymised_24052021/results"

    imNames = ["27513_1998_hands.jpg"] #os.listdir(imLoc)


    for imName in imNames:
        im   = cv2.imread(os.path.join(imLoc,imName),0)
        huo   = huo_method(image=im ,nFingers=10)
        # bin_mask = huo.extract_hand_mask()
        huo(_plot=False)

        ksize=5
        # huo._extract_joint_feature(cs=huo._phalanges[1],_plot=True,ksize=ksize)
        # huo._extract_joint_feature(cs=huo._thumbs[1],_plot=True,ksize=ksize)
        # huo._extract_joint_feature(cs=huo._phalanges[2],_plot=True,ksize=ksize)


        #huo.plot_fingers()
        # for sigma in sigmas:
        #     Gassian_filt = ndi.gaussian_filter(im*bin_mask,sigma=2)

        patches = huo.locate_joints(_plot=True)
        outloc = '/home/amr62/Documents/data/joints'
        for keys,val in huo._joint_patch_library.items():
            joint_name = imName.split(sep='.')[0]+'_'+keys+'.png'
            file_name  = os.path.join(outloc,joint_name)
            print('saving patch at '+file_name)
            # cv2.imwrite(file_name,val)


        for key, val in huo._joint_patch_library.items():
            print(key)

        sigmas = np.arange(20,55,step=5)
        im = huo.image
        truncate = 4.0
        for sigma in sigmas:
            k_size = 2*int(truncate*sigma+0.5)+1
            print("kernel size = {:}".format(k_size))
            t_gauss = time.time()
            gaussian_filt = ndi.gaussian_filter(huo.image * huo._bin_filled_image.astype(np.float),sigma=sigma)
            print("Scipy time taken to apply filter={:}".format(time.time() - t_gauss))
            print("------------------------------------------------------------------")
            t_gauss = time.time()
            t_gaussian_filt = tfa.image.gaussian_filter2d(huo.image * huo._bin_filled_image.astype(np.float),
                                                          filter_shape=[k_size,k_size],sigma=sigma)
            print("Tensorflow time taken to apply filter={:}".format(time.time() - t_gauss))

