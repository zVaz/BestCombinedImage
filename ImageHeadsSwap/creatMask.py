from PIL import Image
import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config
import utils

OUTPUT_DIR = os.path.join(config.IHS_DIR , "output")

nobg = utils.from_json_file(os.path.join(OUTPUT_DIR, "nobg.json"))
image_from = utils.base64_image_to_image(nobg[0]["image_data"])

#Load json file
with open('pface0.json') as f:
    data = json.load(f)

#Set vetices corddinates from json file
top_left = (data["boundingPoly"]["vertices"][0]['x'],data["boundingPoly"]["vertices"][0]['y'])
bottom_right = (data["boundingPoly"]["vertices"][3]['x'],data["boundingPoly"]["vertices"][0]['y'])

    
##get image after removed bg
without_bg_img = Image.open("without-bg.png")
without_bg_img = without_bg_img.convert("RGBA")

##Load original image
img = Image.open("input.png")
img = img.convert("RGBA")
width, height = img.size

#Create new image with original image size
img2 = Image.new('RGB', (width,height), color = (255,255,255))


##scale_w , scale_h = width / without_bg_img.size[0] , height / without_bg_img.size[1]
width, height = without_bg_img.size

pixdata = without_bg_img.load()
pixdata2 = img2.load()
 

# top_left[1],bottom_right[1],1  top_left[0],bottom_right[0],1

for y in range(height):
    for x in range(width):
        if pixdata[x, y][3] == 255:
            pixdata2[x + top_left[0], y + top_left[1]] = (0, 0, 0, 255)


img2.save('myMask.png')