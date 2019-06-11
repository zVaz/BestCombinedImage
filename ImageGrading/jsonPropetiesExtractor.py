import json                      # for json handling
from os import listdir           # for files and system handling
from os.path import isfile, join 

# face class to hold needed properties for each face
class Face():
   def __init__(self, detectionConfidence, blurredLikelihood, headwearLikelihood, joyLikelihood, rollAngle):
      self.detectionConfidence = detectionConfidence
      self.blurredLikelihood = blurredLikelihood
      self.headwearLikelihood = headwearLikelihood
      self.joyLikelihood = joyLikelihood
      self.rollAngle = rollAngle

# path for faces json files
facesPath = '/Users/ggrinber/BestCombinedImage/FacesGroupingFromImage/output'

photoFiles = [f for f in listdir(facesPath) if isfile(join(facesPath, f))]
photoFiles = [i[:1] for i in photoFiles]
photoFiles.remove('d')

# load json file
with open(facesPath + '/data.json', 'r') as f:
    distros_dict = json.load(f)

# extract properties out of json
for i in range(0, int(max(photoFiles))):
    facesList = []
    print("Face number ", i)
# with open('data.json', 'r') as f:
#     distros_dict = json.load(f)
    facesList.append(Face(distros_dict['images'][i]['faces'][i]['detectionConfidence'], 
                          distros_dict['images'][i]['faces'][i]['blurredLikelihood'], 
                          distros_dict['images'][i]['faces'][i]['headwearLikelihood'],
                          distros_dict['images'][i]['faces'][i]['joyLikelihood'],
                          distros_dict['images'][i]['faces'][i]['rollAngle']))

    print("detectionConfidence: ", facesList[i].detectionConfidence)
    print("blurredLikelihood: ", facesList[i].blurredLikelihood)
    print("headwearLikelihood: ", facesList[i].headwearLikelihood)
    print("joyLikelihood: ", facesList[i].joyLikelihood)
    print("rollAngle: ", facesList[i].rollAngle)
