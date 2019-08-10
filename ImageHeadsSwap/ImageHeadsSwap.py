import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.dirname(__file__))
import config
import utils
import creatMask
import bgremove
import inpaintTest
import skimage
from PIL import Image, ImageFilter
from skimage import data, io, color
import numpy as np
from ImageProcessingUtils import inpaint
import math

JSON_DIR   = os.path.join(config.FGFI_DIR, "output")
INPUT_DIR  = os.path.join(config.IMGG_DIR , "output")
RESULT_DIR = os.path.join(config.IHS_DIR, "result")

if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)

def distance(p1, p2):
    return math.sqrt( (p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)

def get_size_from_landmarks(face_data):
    face_right    = next(filter(lambda landmark: landmark["type"] == "RIGHT_EYE_RIGHT_CORNER", face_data["landmarks"]), None)
    face_right    = (face_right["position"]["x"], face_right["position"]["y"])
    face_left     = next(filter(lambda landmark: landmark["type"] == "LEFT_EYE_LEFT_CORNER", face_data["landmarks"]), None)
    face_left     = (face_left["position"]["x"], face_left["position"]["y"])
    face_mid      = next(filter(lambda landmark: landmark["type"] == "MIDPOINT_BETWEEN_EYES", face_data["landmarks"]), None)
    face_mid      = (face_mid["position"]["x"], face_mid["position"]["y"])
    face_nose_tip = next(filter(lambda landmark: landmark["type"] == "NOSE_TIP", face_data["landmarks"]), None)
    face_nose_tip = (face_nose_tip["position"]["x"], face_nose_tip["position"]["y"])

    return distance(face_right, face_left), distance(face_mid, face_nose_tip)

def calc_ratio(data, face, face_to_replace):
    face_data            = data["images"][face["image_index"]]["faces"][face["face_index"]]
    face_to_replace_data = data["images"][face_to_replace["image_index"]]["faces"][face_to_replace["face_index"]]

    face_width, face_height = get_size_from_landmarks(face_data)
    face_to_replace_width, face_to_replace_height = get_size_from_landmarks(face_to_replace_data)

    return face_to_replace_width / float(face_width),  face_to_replace_height / float(face_height)

def get_pos_to_paste(data, face, face_to_replace):
    face_data            = data["images"][face["image_index"]]["faces"][face["face_index"]]
    face_to_replace_data = data["images"][face_to_replace["image_index"]]["faces"][face_to_replace["face_index"]]

    face_data_pos      = {}
    face_data_pos["x"] = face_data["boundingPoly"]["vertices"][0]["x"]
    face_data_pos["y"] = face_data["boundingPoly"]["vertices"][0]["y"]

    face_to_replace_pos      = {}
    face_to_replace_pos["x"] = face_to_replace_data["boundingPoly"]["vertices"][0]["x"]
    face_to_replace_pos["y"] = face_to_replace_data["boundingPoly"]["vertices"][0]["y"]

    print("face_data_pos = {}".format(face_data_pos))
    print("face_to_replace_pos = {}".format(face_to_replace_pos))

    face_nose_tip            = next(filter(lambda landmark: landmark["type"] == "NOSE_TIP", face_data["landmarks"]), None)
    face_to_replace_nose_tip = next(filter(lambda landmark: landmark["type"] == "NOSE_TIP", face_to_replace_data["landmarks"]), None)
    print("face_nose_tip = {}".format(face_nose_tip))
    print("face_to_replace_nose_tip = {}".format(face_to_replace_nose_tip))
    relative_face_nose_tip      = {}
    relative_face_nose_tip["x"] = face_nose_tip["position"]["x"] - face_data_pos["x"]
    relative_face_nose_tip["y"] = face_nose_tip["position"]["y"] - face_data_pos["y"]

    relative_face_to_replace_nose_tip      = {}
    relative_face_to_replace_nose_tip["x"] = face_to_replace_nose_tip["position"]["x"] - face_to_replace_pos["x"]
    relative_face_to_replace_nose_tip["y"] = face_to_replace_nose_tip["position"]["y"] - face_to_replace_pos["y"]
    print("relative_face_nose_tip = {}".format(relative_face_nose_tip))
    print("relative_face_to_replace_nose_tip = {}".format(relative_face_to_replace_nose_tip))

    pos_to_paste      = {}
    pos_to_paste["x"] = face_data_pos["x"] - int(relative_face_to_replace_nose_tip["x"] - relative_face_nose_tip["x"])
    pos_to_paste["y"] = face_data_pos["y"] - int(relative_face_to_replace_nose_tip["y"] - relative_face_nose_tip["y"])
    print("pos_to_paste = {}".format(pos_to_paste))
    return pos_to_paste

def get_faces_to_replace(input_data, data):
    good_image_path = data["images"][input_data["image_index"]]["path"]
    good_image = utils.get_image_by_path(good_image_path, config.FGFI_DIR)

    to_replace = []
    for face_to_replace_info in input_data["faces"]:
        group = data["groups"][face_to_replace_info["group_index"]]
        face_to_replace = group[face_to_replace_info["group_face_index"]]
        for face in group:
            if face["image_index"] == input_data["image_index"]:

                face_image = utils.get_cropped_image(data, face, config.FGFI_DIR)
                f_width, f_height = face_image.size
                print(f_width, f_height)
                face_to_replace_image = utils.get_cropped_image(data, face_to_replace, config.FGFI_DIR)
                fr_width, fr_height = face_to_replace_image.size
                print(fr_width, fr_height)
                width_ratio, height_ratio = calc_ratio(data, face, face_to_replace)
                print("Scaling ratio width {}  height {}".format(width_ratio, height_ratio))
                face_to_replace_image = face_to_replace_image.resize( (int(face_to_replace_image.size[0] * width_ratio), 
                                                                       int(face_to_replace_image.size[1] * height_ratio)) )
                print("face_to_replace_image", face_to_replace_image.size)
                face_image_no_bg = bgremove.removebg(face_image)
                face_image_no_bg = face_image_no_bg.resize(face_image.size)

                face_to_replace_image_bg = bgremove.removebg(face_to_replace_image)
                face_to_replace_image_bg = face_to_replace_image_bg.resize(face_to_replace_image.size)

                face_image_mask = creatMask.copy_face_to_image(good_image, 
                                                                face_image_no_bg , 
                                                                data, face["image_index"], 
                                                                face["face_index"])

                to_replace.append({
                    "face": {
                        "data": face,
                        "image": face_image,
                        "nobg":  face_image_no_bg,
                        "mask": face_image_mask,
                        "image_index": face["image_index"],
                        "face_index": face["face_index"]
                    },
                    "replacer": {
                        "data": face_to_replace,
                        "image": face_to_replace_image,
                        "nobg": face_to_replace_image_bg
                    },
                    "pos_to_replace": get_pos_to_paste(data, face, face_to_replace)
                })
                break
    return to_replace

def main():
    data = utils.from_json_file(os.path.join(JSON_DIR, "data.json"))
    input_data = utils.from_json_file(os.path.join(INPUT_DIR, "input.json"))
    
    good_image_path = data["images"][input_data["image_index"]]["path"]
    good_image = utils.get_image_by_path(good_image_path, config.FGFI_DIR)

    faces_to_replace = get_faces_to_replace(input_data, data)
    
    for i, face_to_replace in enumerate(faces_to_replace):
        print(face_to_replace["face"]["image"].size)
        print(face_to_replace["replacer"]["image"].size)
        print(face_to_replace["face"]["nobg"].size)
        print(face_to_replace["replacer"]["nobg"].size)
    
        width, height = face_to_replace["face"]["image"].size
        radius = math.floor(min(width, height) * 0.018)
        print("width = {}, height = {}, radius = {}".format(width, height, radius))

        
        face_data = data["images"][face_to_replace["face"]["data"]["image_index"]]["faces"][face_to_replace["face"]["data"]["face_index"]]

        good_image, inpainted_mask_image = inpaint(good_image, face_to_replace["face"]["mask"].convert("L"), face_data, radius)
        mask_image      = face_to_replace["face"]["mask"]

        mask_image.save(os.path.join(RESULT_DIR, "mask_{}.png".format(i)))
        good_image.save(os.path.join(RESULT_DIR, "in_{}.png".format(i)))

        x, y = face_to_replace["pos_to_replace"]["x"], face_to_replace["pos_to_replace"]["y"]

        face_image_mask = creatMask.copy_face_to_image_v2(good_image, 
                                                        face_to_replace["replacer"]["nobg"] , 
                                                        x, y, border=True).filter(ImageFilter.GaussianBlur(radius=1))
        face_image      = creatMask.copy_face_to_image_v2(good_image, 
                                                        face_to_replace["replacer"]["nobg"] , 
                                                        x, y, False)

        face_image_mask.save(os.path.join(RESULT_DIR, "fm_{}.png".format(i)))
        face_image.save(os.path.join(RESULT_DIR, "f_{}.png".format(i)))

        good_image = Image.composite(face_image, good_image, face_image_mask.convert("L"))
        good_image.save(os.path.join(RESULT_DIR, "comp_{}.png".format(i)))

if __name__ == "__main__":
    main()