import json
import os
import io
import config
from PIL import Image, ImageDraw
import base64

def base64_image_to_bytes(image64):
    return base64.b64decode(image64.encode("utf-8"))

def base64_image_to_image(image64):
    return Image.open(io.BytesIO(base64_image_to_bytes(image64)))


def from_json_file(path):
    with open(path) as f:
        input = json.load(f)
    return input

def save_to_json_file(path, data):
    with open(path, 'w+') as outfile:
        outfile.write(data)

def image_to_bytes(image, format="png"):
    in_mem_file = io.BytesIO()
    image.save(in_mem_file, format=format)
    return in_mem_file.getvalue()

def crop_image_by_rect(image, vertices):
    box = [(vertex["x"] if "x" in vertex else 0, vertex["y"] if "y" in vertex else 0) for vertex in vertices]
    return image.crop((box[0][0], box[0][1], box[2][0], box[2][1]))

def get_cropped_image(data, to_cropped, basr_dir=""):
    im = get_image_by_path(data["images"][to_cropped["image_index"]]["path"], basr_dir).copy()
    vertices = data["images"][to_cropped["image_index"]]["faces"][to_cropped["face_index"]]["boundingPoly"]["vertices"]
    cropped = crop_image_by_rect(im, vertices)
    return cropped

images_dict = {}
def get_image_by_path(image_path, basr_dir=""):
    if image_path not in images_dict:
        images_dict[image_path] = Image.open(os.path.join(basr_dir, image_path))
    return images_dict[image_path]

def save_groups_to_images(images_info, groups, output_dir):
    for i, group in enumerate(groups):
        for group_image in group:
            im = get_image_by_path(images_info[group_image["image_index"]]["path"]).copy()
            vertices = images_info[group_image["image_index"]]["faces"][group_image["face_index"]]["boundingPoly"]["vertices"]
            cropped = crop_image_by_rect(im, vertices)
            cropped.save(os.path.join(output_dir, "{}_{}_{}.png".format(i,group_image["image_index"], group_image["face_index"])))
