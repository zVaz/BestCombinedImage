import json                      # for json handling
from os import listdir           # for files and system handling
from os.path import isfile, join 

class Face():
   def __init__(self, joyLikelihood, rollAngle):
      self.joyLikelihood = joyLikelihood
      self.rollAngle = rollAngle

facesPath = '../FacesGroupingFromImage/output'

photoFiles = [f for f in listdir(facesPath) if isfile(join(facesPath, f))]
photoFiles = [i[:1] for i in photoFiles]
photoFiles.remove('d')

with open('data.json', 'r') as f:
    distros_dict = json.load(f)

for i in range(0, int(max(photoFiles))):
    facesList = []
    print("Face number ", i)
# with open('data.json', 'r') as f:
#     distros_dict = json.load(f)
    facesList.append(Face(distros_dict['images'][i]['faces'][i]['joyLikelihood'], distros_dict['images'][i]['faces'][i]['rollAngle']))
    print("rollAngle: ", facesList[i].rollAngle)
    print("joyLikelihood: ", facesList[i].joyLikelihood)