import json                      # for json handling
from os import listdir           # for files and system handling
from os.path import isfile, join, dirname
import sys                      # for 'config.py' path
sys.path.append(join(dirname(__file__), '..'))
from config import FGFI_DIR, IMGG_DIR # for paths
import utils

#image attributes
class image_attr(object):
   def __init__(self, sharpness, contrast, brightness):
      self.sharpness = sharpness
      self.contrast = contrast
      self.brighntess = brightness

#image class
class image_class(image_attr):
   def __init__(self, sharpness, contrast, brightness , index):
      super(image_class, self).__init__(sharpness, contrast, brightness)
      self.index = index
      self.grade = 0

   def set_grade(self, grades_weight):
      attributes = [a for a in dir(grades_weight) if not a.startswith('__')]
      for attr in attributes:
         img_attr_value = getattr(self, attr)
         self.grade += img_attr_value * getattr(grades_weight, attr)

# Attributes template (grading json)
class attributesT(object):
   def __init__(self, detectionConfidence, blurredLikelihood, OpenEyesConfidence, joyLikelihood):
      self.detectionConfidence = detectionConfidence
      self.blurredLikelihood = blurredLikelihood
      self.OpenEyesConfidence = OpenEyesConfidence
      self.joyLikelihood = joyLikelihood

# Faces data
class attributesI(attributesT):
   # for attributes which likely is good fo them
   strToGradeGood = { 'VERY_UNLIKELY' : 1,
                'UNLIKELY': 2,
                'POSSIBLE' : 3,
                'LIKELY' : 4,
                'VERY_LIKELY' : 5,
                'UNKOWN' : 0 }

   # for attributes which likely is bad fo them
   strToGradeBad = { 'VERY_UNLIKELY' : 1,
               'UNLIKELY': 2,
               'POSSIBLE' : 3,
               'LIKELY' : 4,
               'VERY_LIKELY' : 5,
               'UNKOWN' : 0 }

   # attributed for 'strToGradeGood'
   good_attr = ['joyLikelihood']
   # attributed for 'strToGradeBad'
   bad_attr = ['blurredLikelihood']

   def __init__(self, detectionConfidence, blurredLikelihood, OpenEyesConfidence, joyLikelihood, face_info):
      super(attributesI, self).__init__(detectionConfidence, blurredLikelihood, OpenEyesConfidence, joyLikelihood)
      self.face_info = face_info
      self.grade = 0
      
   def set_grade(self, grades_weight):
      attributes = [a for a in dir(grades_weight) if not a.startswith('__')]
      for attr in attributes:
         faceAttrValue = getattr(self, attr)
         # if attribute is a likeliness string, got to dict
         if type(faceAttrValue) is str:
            if faceAttrValue in attributesI.good_attr:
               self.grade += attributesI.strToGradeGood[faceAttrValue] * getattr(grades_weight, attr)
            else:
               self.grade += attributesI.strToGradeBad[faceAttrValue] * getattr(grades_weight, attr)
         else:
               self.grade += faceAttrValue * getattr(grades_weight, attr)

# extract updated grades for properties
def getUpdatedGradesWeight():
    # load face properties grades weight json
    with open(IMGG_DIR + '/propGrades.json', 'r') as f:
       grade_weight_json = json.load(f)

    print(grade_weight_json['properties'][0]['OpenEyesConfidence'])

    face_attrs = attributesT(grade_weight_json['properties'][0]['detectionConfidence'], 
                       grade_weight_json['properties'][0]['blurredLikelihood'], 
                       grade_weight_json['properties'][0]['OpenEyesConfidence'],
                       grade_weight_json['properties'][0]['joyLikelihood'])

   # load image properties grades weight json
    with open(IMGG_DIR + '/imgPropGrades.json', 'r') as f:
       image_weight_json = json.load(f)

    img_attrs = image_attr(image_weight_json['properties'][0]['sharpness'], 
                  image_weight_json['properties'][0]['contrast'], 
                  image_weight_json['properties'][0]['brightness'])

    return face_attrs, img_attrs

# get image properties to object
def imageToClass(image_prop, index):
      return image_class(image_prop["sharpness"],
                         image_prop["contrast"],
                         image_prop["brightness"],
                         index)

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
            res[-1].append(attributesI(face_data["detectionConfidence"], face_data["blurredLikelihood"], 0, face_data["joyLikelihood"], face))
            # check faces
            #im = utils.get_cropped_image(image_data_json, face)

    return res