import json                      # for json handling
from os import listdir           # for files and system handling
from os.path import isfile, join 
import sys                      # for 'config.py' path
sys.path.insert(0, '/Users/ggrinber/BestCombinedImage/')
from config import BASE_DIR, IMGG_DIR # for paths

# Attributes template
class attributesT():
   def __init__(self, detectionConfidence, blurredLikelihood, headwearLikelihood, joyLikelihood, rollAngle):
      self.detectionConfidence = detectionConfidence
      self.blurredLikelihood = blurredLikelihood
      self.headwearLikelihood = headwearLikelihood
      self.joyLikelihood = joyLikelihood
      self.rollAngle = rollAngle

# get all output files
photoFiles = [i[:1] for i in [f for f in listdir(BASE_DIR + '/output/') if isfile(join(BASE_DIR + '/output/', f))]]
photoFiles.remove('d')

numOfPhotos = int(max(photoFiles))

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
    with open(BASE_DIR + '/output/data.json', 'r') as f:
        image_data_json = json.load(f)

    numOfFaces = len(image_data_json['images'][0]['faces'])

    facesList = [[0]*numOfPhotos for i in range(numOfFaces)]
    for photoIndex in range(0, numOfPhotos):
        for i in range(0, numOfFaces):
            #print("Face number ", i)
            # add face number i
            facesList[photoIndex][i] = attributesT(image_data_json['images'][photoIndex]['faces'][i]['detectionConfidence'], 
                                        image_data_json['images'][photoIndex]['faces'][i]['blurredLikelihood'], 
                                        image_data_json['images'][photoIndex]['faces'][i]['headwearLikelihood'],
                                        image_data_json['images'][photoIndex]['faces'][i]['joyLikelihood'],
                                        image_data_json['images'][photoIndex]['faces'][i]['rollAngle'])
    return facesList
