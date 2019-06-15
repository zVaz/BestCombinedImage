from os.path import isfile, join, dirname
import sys                      # for 'config.py' path
sys.path.append(dirname(__file__))
from jsonExtractor import extractFacesProperties, getUpdatedGradesWeight, IMGG_DIR
import json
import utils
import os
import operator

OUTPUT_DIR = os.path.join(IMGG_DIR, "output")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def main():
    # likeliness to grade weight dict   
    strToGrade = { 'VERY_UNLIKELY' : 1,
                    'UNLIKELY': 2,
                    'POSSIBLE' : 3,
                    'LIKELY' : 4,
                    'VERY_LIKELY' : 5,
                    'UNKOWN' : 0 }

    # get updated faces properties and grade weight
    groups = extractFacesProperties()
    grades_weight = getUpdatedGradesWeight()

    # initialize faceGrades
    #faceGrades = [[0]*len(faces) for i in range(len(faces[0]))]
    # get attributes to iterate over
    #attributes = [a for a in dir(grades_weight) if not a.startswith('__')]

    best_faces = []

    for group in groups:
        for face in group:
            face.set_grade(grades_weight)
        best_faces.append(max(group, key = lambda face: face.grade).face_info)

    count_bet_faces_in_image = {}
    for best_face in best_faces:
        curr = count_bet_faces_in_image.get(best_face["image_index"], 0)
        count_bet_faces_in_image[best_face["image_index"]] = curr + 1

    print(count_bet_faces_in_image)
    best_image_index = max(count_bet_faces_in_image.items(), key = operator.itemgetter(1))[0]

    faces_to_swap = []
    for best_face in best_faces:
        if best_face["image_index"] != best_image_index:
            faces_to_swap.append({
                    "group_index": best_face["group_index"],
                    "group_face_index": best_face["group_face_index"]
            })

    utils.save_to_json_file(os.path.join(OUTPUT_DIR, "input.json"), 
                            json.dumps( {
                                        "image_index": best_image_index,
                                        "faces": faces_to_swap
                                        }))