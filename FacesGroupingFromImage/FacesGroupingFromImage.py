from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw
import boto3
import os

from google.protobuf.json_format import MessageToJson

dir_path = os.path.dirname(os.path.realpath(__file__))

AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
GOOGLE_APPLICATION_CREDENTIALS_PATH = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

AMAZON_CLIENT = boto3.client('rekognition', region_name='us-west-2',
                                aws_access_key_id=AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

IMAGES_DIR = "./images/"
CROPPED_DIR = "./cropped/"
GROUPS_DIR = "./groups/"

if not os.path.exists(os.path.dirname(IMAGES_DIR)):
    os.makedirs(os.path.dirname(IMAGES_DIR))
if not os.path.exists(os.path.dirname(CROPPED_DIR)):
    os.makedirs(os.path.dirname(CROPPED_DIR))
if not os.path.exists(os.path.dirname(GROUPS_DIR)):
    os.makedirs(os.path.dirname(GROUPS_DIR))

def detect_face(face_file, max_results=4):
    client = vision.ImageAnnotatorClient()
    content = face_file.read()
    image = types.Image(content=content)
    return client.face_detection(image=image, max_results=max_results).face_annotations

def crop_faces(image, faces, output_filename, input_filename):
    im = Image.open(image)
    for index, face in enumerate(faces):
        cropped = im.copy()
        box = [(vertex.x, vertex.y)
               for vertex in face.bounding_poly.vertices]
        cropped = cropped.crop((box[0][0], box[0][1], box[2][0], box[2][1]))
        name = "{}face{}".format(os.path.basename(input_filename)[0], index)
        cropped.save(os.path.join(CROPPED_DIR, "{}.jpg".format(name)))
        with open(os.path.join(CROPPED_DIR, "{}.json".format(name)), 'w+') as outfile:
            outfile.write(MessageToJson(face))

def get_images():
    images = []
    for filename in os.listdir(IMAGES_DIR):
        file_path = os.path.join(IMAGES_DIR, filename)
        if os.path.isfile(file_path) and filename[0] != ".":
            images.append(file_path)
    return images

def get_cropped_images():
    cropped = []
    for filename in os.listdir(CROPPED_DIR):
        file_path = os.path.join(CROPPED_DIR, filename)
        if os.path.isfile(file_path) and filename[0] != "." and os.path.splitext(filename)[1] == ".jpg":
            cropped.append(file_path)
    return cropped

def get_cropped_images_groups():
    groups = {}
    cat = 0
    for filename in cropped:
        if filename not in groups:
            with open(filename, 'rb') as imageSource:
                groups[filename] = cat
                for filename2 in cropped:
                    imageSource.seek(0)
                    if filename2 not in groups:
                        with open(filename2, 'rb') as imageTarget:
                            response = AMAZON_CLIENT.compare_faces(SimilarityThreshold=70,
                                                            SourceImage={
                                                                'Bytes': imageSource.read()},
                                                            TargetImage={'Bytes': imageTarget.read()})
                            if len(response['FaceMatches']) > 0 and response['FaceMatches'][0]['Face']['Confidence'] >= 40:
                                groups[filename2] = cat
            cat += 1
    return groups

def crop_faces_from_images(images):
    for filename in images:
        print(filename)
        with open(filename, 'rb') as image:
            output_filename = "out.jpg"
            faces = detect_face(image, 10)
            print('Found {} face{}'.format(
                  len(faces), '' if len(faces) == 1 else 's'))
            # Reset the file pointer, so we can read the file again
            image.seek(0)
            crop_faces(image, faces, output_filename, filename)

def move_cropped_images_to_groups_directory(groups):
    for filename, group in groups.items():
        curr_dir = os.path.join(GROUPS_DIR, str(group))
        if not os.path.isdir(curr_dir):
            os.mkdir(curr_dir)
        base = os.path.splitext(os.path.basename(filename))[0]
        json = os.path.splitext(filename)[0] + ".json"

        print(filename, os.path.join(curr_dir, base))
        os.rename(filename, os.path.join(curr_dir, base + ".jpg"))
        os.rename(json, os.path.join(curr_dir, base + ".json"))
        
if __name__ == '__main__':
    images = get_images()
    crop_faces_from_images(images)
    cropped = get_cropped_images()
    groups = get_cropped_images_groups()
    move_cropped_images_to_groups_directory(groups)
    
