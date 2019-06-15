from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw
import boto3
import os, io, sys
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config
import utils

from google.protobuf.json_format import MessageToJson

dir_path = os.path.dirname(os.path.realpath(__file__))

AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]

AMAZON_CLIENT = boto3.client('rekognition', region_name='us-west-2',
                                aws_access_key_id=AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

INPUT_DIR   = os.path.join(config.FGFI_DIR, "input")
OUTPUT_DIR   = os.path.join(config.FGFI_DIR, "output")

if not os.path.exists(os.path.dirname(INPUT_DIR)):
    os.makedirs(os.path.dirname(INPUT_DIR))
if not os.path.exists(os.path.dirname(OUTPUT_DIR)):
    os.makedirs(os.path.dirname(OUTPUT_DIR))

def get_images():
    images = []
    for filename in os.listdir(INPUT_DIR):
        file_path = os.path.join(INPUT_DIR, filename)
        if os.path.isfile(file_path) and filename[0] != ".":
            images.append(file_path)
    return images

def detect_face(face_file, max_results=4):
    client = vision.ImageAnnotatorClient()
    content = face_file.read()
    image = types.Image(content=content)
    return client.face_detection(image=image, max_results=max_results)

def crop_faces_from_images(images):
    images_info = []
    for filename in images:
        print(filename)
        with open(filename, 'rb') as image:
            faces = detect_face(image, 10)
            images_info.append({
                "path": filename,
                "faces": json.loads(MessageToJson(faces))["faceAnnotations"]
            })
            print('Found {} face{}'.format(
                  len(images_info[-1]["faces"]), '' if len(images_info[-1]["faces"]) == 1 else 's'))
    return images_info

def detect_properties(images):
    """Detects image properties in the file."""
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()

    for pic in images:
        with io.open(pic, 'rb') as image_file:
            content = image_file.read()

        image = vision.types.Image(content=content)

        response = client.image_properties(image=image)

        utils.save_to_json_file(os.path.join(OUTPUT_DIR, pic.split("/input/")[1].split(".")[0] + ".json"), 
                        MessageToJson(response))

def get_cropped_faces(images_info):
    faces_info = []
    for image_index, image in enumerate(images_info):
        for face_index, face in enumerate(image["faces"]):
            copy = utils.get_image_by_path(image["path"]).copy()
            faces_info.append({
                "image_index": image_index,
                "face_index" : face_index,
                "face"       : utils.crop_image_by_rect(copy, 
                                                        face["boundingPoly"]["vertices"])
            })
    return faces_info



def to_group_index(image_index, face_index):
    return "{}_{}".format(image_index, face_index)

def get_cropped_images_groups(images_info):
    groups = {}
    cat = 0
    faces_info = get_cropped_faces(images_info)
    for face_info in faces_info:
        if to_group_index(face_info["image_index"], face_info["face_index"]) not in groups:
            groups[to_group_index(face_info["image_index"], face_info["face_index"])] = cat
            for face_info2 in faces_info:
                if to_group_index(face_info2["image_index"], face_info2["face_index"]) not in groups:
                    response = AMAZON_CLIENT.compare_faces(SimilarityThreshold=70,
                                                        SourceImage={
                                                            'Bytes': utils.image_to_bytes(face_info["face"])
                                                        },
                                                        TargetImage={
                                                            'Bytes': utils.image_to_bytes(face_info2["face"])
                                                        })
                    if len(response['FaceMatches']) > 0 and response['FaceMatches'][0]['Face']['Confidence'] >= 40:
                        groups[to_group_index(face_info2["image_index"], face_info2["face_index"])] = cat
            cat += 1  
    return groups

def main():
    images = get_images()
    
    images_info = crop_faces_from_images(images)
    groups_dict = get_cropped_images_groups(images_info)

    #Convert groups to list of dictionary
    groups = [[] for i in range(len(set(groups_dict.values())))]
    for image_face_index, group_index in groups_dict.items():
        image_index, face_index = image_face_index.split("_")
        groups[group_index].append({
            "image_index": int(image_index),
            "face_index" : int(face_index)
        })

    #Save the data to file
    utils.save_to_json_file(os.path.join(OUTPUT_DIR, "data.json"), 
                            json.dumps( {
                                            "images": images_info,
                                            "groups": groups
                                        }))

    detect_properties(images)

if __name__ == "__main__":
    main()