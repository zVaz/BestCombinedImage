import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config
import utils
import creatMask
import bgremove
import inpaintTest
import skimage
from PIL import Image, ImageFilter
from skimage import data, io, color
import numpy as np

JSON_DIR   = os.path.join(config.FGFI_DIR, "output")
INPUT_DIR  = os.path.join(config.IHS_DIR , "debug")
RESULT_DIR = os.path.join(config.IHS_DIR, "result")

if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)

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
                ratio = f_height / float(fr_height)
                print("Scaling ratio {}".format(ratio))
                face_to_replace_image = face_to_replace_image.resize( [int(ratio * s) for s in face_to_replace_image.size] )
                print("face_to_replace_image", face_to_replace_image.size)
                face_image_no_bg = bgremove.removebg(face_image)
                face_to_replace_image_bg = bgremove.removebg(face_to_replace_image)
                print("face_to_replace_image_bg", face_to_replace_image_bg.size)
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
                    }
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
        inpainted_array, mask_array = inpaintTest.inpaint_image(good_image, face_to_replace["face"]["mask"])
        inpainted_image = Image.fromarray(skimage.util.img_as_ubyte(inpainted_array))
        mask_image      = Image.fromarray(skimage.util.img_as_ubyte(mask_array))
        inpainted_image.save(os.path.join(RESULT_DIR, "in_{}.png".format(i)))
        mask_image.save(os.path.join(RESULT_DIR, "mask_{}.png".format(i)))

        face_image_mask = creatMask.copy_face_to_image(good_image, 
                                                        face_to_replace["replacer"]["nobg"] , 
                                                        data, face_to_replace["face"]["image_index"], 
                                                        face_to_replace["face"]["face_index"]).filter(ImageFilter.GaussianBlur(radius=2))
        face_image      = creatMask.copy_face_to_image(good_image, 
                                                        face_to_replace["replacer"]["nobg"] , 
                                                        data, face_to_replace["face"]["image_index"], 
                                                        face_to_replace["face"]["face_index"], False)
        face_image_mask.save(os.path.join(RESULT_DIR, "fm_{}.png".format(i)))
        face_image.save(os.path.join(RESULT_DIR, "f_{}.png".format(i)))
        comp = Image.composite(face_image, inpainted_image, face_image_mask.convert("L"))
        comp.save(os.path.join(RESULT_DIR, "comp_{}.png".format(i)))

if __name__ == "__main__":
    main()