from os.path import isfile, join, dirname
import sys                      # for 'config.py' path
sys.path.append(dirname(__file__))
from jsonExtractor import extractFacesProperties, getUpdatedGradesWeight, IMGG_DIR, FGFI_DIR, imageToClass
from ImageGrading.imageQualityDetection import set_image_properties
import json
import utils
import os
import operator

OUTPUT_DIR = os.path.join(IMGG_DIR, "output")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def main():
    # get updated faces properties and grade weight
    groups = extractFacesProperties()
    face_attrs, img_attrs = getUpdatedGradesWeight()

    best_faces = []

    for group in groups:
        for face in group:
            face.set_grade(face_attrs)
        best_faces.append(max(group, key = lambda face: face.grade).face_info)

    count_bet_faces_in_image = {}

    for best_face in best_faces:
        curr = count_bet_faces_in_image.get(best_face["image_index"], 0)
        count_bet_faces_in_image[best_face["image_index"]] = curr + 1

    print(count_bet_faces_in_image)
    # get images with the highest number of good faces
    best_image_index = [k for k,v in count_bet_faces_in_image.items() if v == max(count_bet_faces_in_image.values())]

    # if there are more than 1 image with highest number of good faces
    if len(best_image_index) > 1:
        with open(FGFI_DIR + '/output/data.json', 'r') as f:
            image_data_json = json.load(f)
        best_images_props = []
        best_images = []
        for best_image in best_image_index:
            best_images_props.append(set_image_properties(image_data_json["images"][best_image]["path"]))
            best_images.append(imageToClass(best_images_props[best_image], best_image))
        for image_prop in best_images:
            image_prop.set_grade(img_attrs)
        best_image_index = max(best_images, key=operator.attrgetter('grade')).index
    else:
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