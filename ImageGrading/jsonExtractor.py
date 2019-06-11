import json                      # for json handling
from os import listdir           # for files and system handling
from os.path import isfile, join 

# face class to hold needed properties for each face
class attributesT():
   def __init__(self, detectionConfidence, blurredLikelihood, headwearLikelihood, joyLikelihood, rollAngle):
      self.detectionConfidence = detectionConfidence
      self.blurredLikelihood = blurredLikelihood
      self.headwearLikelihood = headwearLikelihood
      self.joyLikelihood = joyLikelihood
      self.rollAngle = rollAngle

# path for project home foler
homePath = '/Users/ggrinber/BestCombinedImage/'
# path for 1st part output jsons
facesPath = homePath + 'FacesGroupingFromImage/output'
# path for properties grades json
propGradesPath = homePath + 'ImageGrading/propGrades.json'

# get all output files
photoFiles = [i[:1] for i in [f for f in listdir(facesPath) if isfile(join(facesPath, f))]]
photoFiles.remove('d')

# extract updated grades for properties
def getGradesWeight():
    # load properties grades weight json
    with open(propGradesPath, 'r') as f:
       grade_weight_json = json.load(f)

    return attributesT(grade_weight_json['properties'][0]['detectionConfidence'], 
                       grade_weight_json['properties'][0]['blurredLikelihood'], 
                       grade_weight_json['properties'][0]['headwearLikelihood'],
                       grade_weight_json['properties'][0]['joyLikelihood'],
                       grade_weight_json['properties'][0]['rollAngle'])

# extract properties out of json
def extractFacesProperties():
    # load image data json
    with open(facesPath + '/data.json', 'r') as f:
        image_data_json = json.load(f)

    for i in range(0, int(max(photoFiles))):
        facesList = []
        print("Face number ", i)
        # add face number i
        facesList.append(attributesT(image_data_json['images'][i]['faces'][i]['detectionConfidence'], 
                                     image_data_json['images'][i]['faces'][i]['blurredLikelihood'], 
                                     image_data_json['images'][i]['faces'][i]['headwearLikelihood'],
                                     image_data_json['images'][i]['faces'][i]['joyLikelihood'],
                                     image_data_json['images'][i]['faces'][i]['rollAngle']))

        return facesList
