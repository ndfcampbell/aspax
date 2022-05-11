

import os,h5py


class SCORE_PROFILE(object):
    def __init__(self,matFile):
        pass


def create_profile(name,damage_types,damage_scores,damage_areas,loc='score_profiles'):
    """

    :param name: name of the coring techniques eg Ratingen, VdH-PsA, PsA-MSS, Steinbrocker
    :param damage_types: tuple like of string for the feature being described e.g. ['erosion','JSN']
    :param damage_scores: tuple of interval for discrete range of score values e.g. [(0,5),(0,3)] represents
                          0,1,2,3,4,5 and 0,1,2,3
    :return:
    """
    mylib = {}
    assert len(damage_types)==len(damage_scores)
    if not os.path.isdir(loc): os.makedirs(loc)
    mylib['damage_types']  = damage_types
    mylib['damage_scores'] =  damage_scores
    mylib['damage_areas']  = damage_areas
    hf = h5py.File(os.path.join(loc,name+'.h5'),'w')
    #Store this dictionary object as hdf5 metadata
    for k in mylib.keys():
        print(k)
        hf.attrs[k] = mylib[k]
    hf.close()



def load_profile(profile_loc):
    f = h5py.File(profile_loc,'r')
    my_lib = {}
    for k in f.attrs.keys():
        my_lib[k] = f.attrs[k]
    my_lib['name'] = profile_loc.split('/')[-1].split('.')[0]
    f.close()
    return my_lib


if __name__=='__main__':
    # outloc = '/home/adwaye/PycharmProjects/aspax/config'
    # names              = ['Steinbrocker','PsA-MSS','VdH-PsA','Ratingen']
    # damage_types_array = [['Damage'],
    #                       ['Erosion','JSN'],
    #                       ['Erosion','JSN'],
    #                       ['Destruction','Proliferation']
    #                       ]
    # damage_scores_array = [[(0,4)],
    #                        [(0,5),(0,5)],
    #                        [(0,3),(0,4)],
    #                        [(0,5),(0,5)],
    #                        ]
    # damage_areas = []
    # for name in names:
    #     area_loc  = "config"
    #     text_file = open(os.path.join(name+'_areas.txt'))
    #     lines     = text_file.readline().split(",")
    #     damage_areas+=[lines]
    #     text_file.close()
    # for name,damage_types,damage_scores,damage_area in zip(names,damage_types_array,damage_scores_array,damage_areas):
    #     create_profile(name,damage_types,damage_scores,damage_areas=damage_area,loc = "./")
    name = 'Monitor'
    damage_types = ['s-vdH_Erosion','s-vdH_JSN','ratingen_osteoProlif']





