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

def detect_face(face_file, max_results=4):
    client = vision.ImageAnnotatorClient()
    content = face_file.read()
    image = types.Image(content=content)
    return client.face_detection(image=image, max_results=max_results).face_annotations



def highlight_faces(image, faces, output_filename, input_filename):
    im = Image.open(image)
    draw = ImageDraw.Draw(im)
    print(os.path.basename(input_filename))
    for index, face in enumerate(faces):
        cropped = im.copy()
        box = [(vertex.x, vertex.y)
               for vertex in face.bounding_poly.vertices]
        cropped = cropped.crop((box[0][0], box[0][1], box[2][0], box[2][1]))
        name = "{}face{}".format(os.path.basename(input_filename)[0], index)
        cropped.save("./cropped/{}.jpg".format(name))
        
        with open("./cropped/{}.json".format(name), 'w+') as outfile:
           outfile.write(MessageToJson(face))

if __name__ == '__main__':
   images_dir = "./images/"
   if not os.path.exists(os.path.dirname(images_dir)):
        os.makedirs(os.path.dirname(images_dir))
   images = []
   
   for filename in os.listdir(images_dir):
      file_path = os.path.join(images_dir,filename)
      if os.path.isfile(file_path) and filename[0] != ".":
         images.append(file_path)
   
   for filename in images:
      print(filename)
      with open(filename, 'rb') as image:
         output_filename = "out.jpg"
         faces = detect_face(image, 10)
         print('Found {} face{}'.format(len(faces), '' if len(faces) == 1 else 's'))
         # Reset the file pointer, so we can read the file again
         image.seek(0)
         highlight_faces(image, faces, output_filename, filename)

   cropped_dir = "./cropped/"
   if not os.path.exists(os.path.dirname(cropped_dir)):
        os.makedirs(os.path.dirname(cropped_dir))
   cropped = []
   
   for filename in os.listdir(cropped_dir):
      file_path = os.path.join(cropped_dir, filename)
      if os.path.isfile(file_path) and filename[0] != "." and os.path.splitext(filename)[1] == ".jpg":
         cropped.append(file_path)
   
   client=boto3.client('rekognition', region_name='us-west-2',
                        aws_access_key_id=AWS_ACCESS_KEY_ID, 
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
   
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
                     response=client.compare_faces(SimilarityThreshold=70,
                                             SourceImage={'Bytes': imageSource.read()},
                                             TargetImage={'Bytes': imageTarget.read()})
                     if len(response['FaceMatches']) > 0 and response['FaceMatches'][0]['Face']['Confidence'] >= 40:
                        groups[filename2] = cat
         cat += 1

   groups_dir = "./groups/"
   if not os.path.exists(os.path.dirname(groups_dir)):
        os.makedirs(os.path.dirname(groups_dir))

   for filename, group in groups.items():
      curr_dir = os.path.join(groups_dir, str(group))
      if not os.path.isdir(curr_dir):
         os.mkdir(curr_dir)
      base = os.path.splitext(os.path.basename(filename))[0]
      json = os.path.splitext(filename)[0] + ".json"

      print(filename, os.path.join(curr_dir, base))
      os.rename(filename, os.path.join(curr_dir, base + ".jpg"))
      os.rename(json, os.path.join(curr_dir, base + ".json"))