import json                      # for json handling
from os import listdir           # for files and system handling
from os.path import isfile, join 

# face class to hold needed properties for each face
class Face():
   def __init__(self, joyLikelihood, rollAngle):
      self.joyLikelihood = joyLikelihood
      self.rollAngle = rollAngle

# path for faces json files
facesPath = '../FacesGroupingFromImage/output'

photoFiles = [f for f in listdir(facesPath) if isfile(join(facesPath, f))]
photoFiles = [i[:1] for i in photoFiles]
photoFiles.remove('d')

# load json file
with open('data.json', 'r') as f:
    distros_dict = json.load(f)

# extract properties out of json
for i in range(0, int(max(photoFiles))):
    facesList = []
    print("Face number ", i)
# with open('data.json', 'r') as f:
#     distros_dict = json.load(f)
    facesList.append(Face(distros_dict['images'][i]['faces'][i]['joyLikelihood'], distros_dict['images'][i]['faces'][i]['rollAngle']))
    print("rollAngle: ", facesList[i].rollAngle)
    print("joyLikelihood: ", facesList[i].joyLikelihood)