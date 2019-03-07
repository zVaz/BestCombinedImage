from PIL import Image
import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config
import utils
import base64

OUTPUT_DIR         = os.path.join(config.IHS_DIR , "output")
DEBUG_DIR          = os.path.join(config.IHS_DIR , "debug")
FGFI_OUTPUT__DIR   = os.path.join(config.FGFI_DIR, "debug")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Image without bg



# Get


nobg = utils.from_json_file(os.path.join(DEBUG_DIR, "nobg.json"))

#get path for original image
image_index = nobg[1]["info"]["image_index"]
face_index = nobg[1]["info"]["face_index"]
data = utils.from_json_file(os.path.join(FGFI_OUTPUT__DIR, "data.json"))
path_for_image = data["images"][image_index]["path"]
img = utils.get_image_by_path(path_for_image, config.FGFI_DIR)
img = img.convert("RGBA")
width, height = img.size
#Load json file

vertices = data["images"][image_index]["faces"][face_index]["boundingPoly"]["vertices"]

#Set vetices corddinates from json file
top_left = (vertices[0]['x'], vertices[0]['y'])
bottom_right = (vertices[3]['x'], vertices[3]['y'])

    
##get image after removed bg
#without_bg_img = Image.open("without-bg.png")
nobg = utils.from_json_file(os.path.join(DEBUG_DIR, "nobg.json"))
image_from = utils.base64_image_to_image(nobg[1]["image_data"])
without_bg_img = image_from.convert("RGBA")



#Create new image with original image size
img2 = Image.new('RGB', (width,height), color = (255,255,255))


##scale_w , scale_h = width / without_bg_img.size[0] , height / without_bg_img.size[1]
width, height = without_bg_img.size

pixdata = without_bg_img.load()
pixdata2 = img2.load()
 

# top_left[1],bottom_right[1],1  top_left[0],bottom_right[0],1


for y in range(height):
    for x in range(width):
        pixdata[x, y] = (0, 0, 0, 255) if pixdata[x, y][3] == 255 else (255, 255, 255, 255)

img2.paste(without_bg_img, top_left)

#Save image
img2.save(os.path.join(OUTPUT_DIR, "myMask.png"))

#Save to json file the mask
nobg[1]["mask"] = utils.image_to_base64_image(img2)
utils.save_to_json_file(os.path.join(OUTPUT_DIR, "nobg_mask.json"), json.dumps(nobg))
