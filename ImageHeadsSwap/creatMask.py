from PIL import Image, ImageDraw
import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config
import utils
import base64


def copy_face_to_image(img , image_from , data, image_index, face_index, masked = True, border = False):
   

    ###############################################################################

    vertices = data["images"][image_index]["faces"][face_index]["boundingPoly"]["vertices"]

    #Set vetices corddinates from json file
    x = vertices[0]['x'] + (abs(image_from.size[0] - abs(vertices[1]['x'] - vertices[0]['x'])) // 2)
    y = vertices[0]['y'] + (abs(image_from.size[1] - abs(vertices[2]['y'] - vertices[1]['y'])) // 2)
    top_left = (x, y)

    without_bg_img = image_from.convert("RGBA")

    width, height = img.size

    #Create new image with original image size
    img2 = Image.new('RGB', (width,height), color = (0,0,0))

    width, height = without_bg_img.size
    pixdata = without_bg_img.load()

    if masked:
        for y in range(height):
            for x in range(width):
                pixdata[x, y] = (255, 255, 255, 255) if pixdata[x, y][3] == 255 else (0, 0, 0, 255)

    if border:
        d = ImageDraw.Draw(without_bg_img)
        d.rectangle([0,0,without_bg_img.width,without_bg_img.height], width = 7, outline="#000000")

    img2.paste(without_bg_img, top_left)

    return img2

if __name__ == "__main__":
    OUTPUT_DIR         = os.path.join(config.IHS_DIR , "output")
    DEBUG_DIR          = os.path.join(config.IHS_DIR , "debug")
    FGFI_OUTPUT__DIR   = os.path.join(config.FGFI_DIR, "debug")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    nobg = utils.from_json_file(os.path.join(DEBUG_DIR, "nobg.json"))

    #get path for original image
    image_index = nobg[1]["info"]["image_index"]
    face_index = nobg[1]["info"]["face_index"]
    data = utils.from_json_file(os.path.join(FGFI_OUTPUT__DIR, "data.json"))
    path_for_image = data["images"][image_index]["path"]
    img = utils.get_image_by_path(path_for_image, config.FGFI_DIR)
    img = img.convert("RGBA")
    width, height = img.size
        
    ##get image after removed bg
    nobg = utils.from_json_file(os.path.join(DEBUG_DIR, "nobg.json"))
    image_from = utils.base64_image_to_image(nobg[1]["image_data"])

    creat_mask(img , image_from , data )
