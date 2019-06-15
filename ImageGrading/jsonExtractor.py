import json                      # for json handling
from os import listdir           # for files and system handling
from os.path import isfile, join, dirname
import sys                      # for 'config.py' path
sys.path.append(join(dirname(__file__), '..'))
from config import FGFI_DIR, IMGG_DIR # for paths
import utils

# Attributes template (grading json)
class attributesT(object):
   def __init__(self, detectionConfidence, blurredLikelihood, headwearLikelihood, joyLikelihood, rollAngle):
      self.detectionConfidence = detectionConfidence
      self.blurredLikelihood = blurredLikelihood
      self.headwearLikelihood = headwearLikelihood
      self.joyLikelihood = joyLikelihood
      self.rollAngle = rollAngle

# Faces data
class attributesI(attributesT):
   strToGrade = { 'VERY_UNLIKELY' : 1,
                'UNLIKELY': 2,
                'POSSIBLE' : 3,
                'LIKELY' : 4,
                'VERY_LIKELY' : 5,
                'UNKOWN' : 0 }

   def __init__(self, detectionConfidence, blurredLikelihood, headwearLikelihood, joyLikelihood, rollAngle, face_info):
      super(attributesI, self).__init__(detectionConfidence, blurredLikelihood, headwearLikelihood, joyLikelihood, rollAngle)
      self.face_info = face_info
      self.grade = 0
      
   def set_grade(self, grades_weight):
      attributes = [a for a in dir(grades_weight) if not a.startswith('__')]
      for attr in attributes:
         faceAttrValue = getattr(self, attr)
         # if attribute is a likeliness string, got to dict
         if type(faceAttrValue) is str:
               self.grade += attributesI.strToGrade[faceAttrValue] * getattr(grades_weight, attr)
         else:
               self.grade += faceAttrValue * getattr(grades_weight, attr)


# get all output files
photoFiles = [i[:1] for i in [f for f in listdir(FGFI_DIR + '/output/') if isfile(join(FGFI_DIR + '/output/', f))]]
photoFiles.remove('d')

#numOfPhotos = int(max(photoFiles))

# extract updated grades for properties
def getUpdatedGradesWeight():
    # load properties grades weight json
    with open(IMGG_DIR + '/propGrades.json', 'r') as f:
       grade_weight_json = json.load(f)

    return attributesT(grade_weight_json['properties'][0]['detectionConfidence'], 
                       grade_weight_json['properties'][0]['blurredLikelihood'], 
                       grade_weight_json['properties'][0]['headwearLikelihood'],
                       grade_weight_json['properties'][0]['joyLikelihood'],
                       grade_weight_json['properties'][0]['rollAngle'])

# extract properties out of json
def extractFacesProperties():
    # load image data json
    with open(FGFI_DIR + '/output/data.json', 'r') as f:
        image_data_json = json.load(f)

    res = []
    groups = image_data_json["groups"]
    

    for group_index, group in enumerate(groups):
        res.append([])
        for group_face_index, face in enumerate(group):
            image_index = face["image_index"]
            face_index  = face["face_index"]

            image_data = image_data_json['images'][image_index]
            face_data = image_data['faces'][face_index]
            face["group_index"] = group_index
            face["group_face_index"] = group_face_index
            res[-1].append(attributesI(face_data["detectionConfidence"], face_data["blurredLikelihood"], face_data["headwearLikelihood"], face_data["joyLikelihood"], face_data["rollAngle"], face))

            im = utils.get_cropped_image(image_data_json, face)

    return res