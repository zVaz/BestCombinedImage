# Requires "requests" to be installed (see python-requests.org)
import requests
import os
import io
import sys
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config
import utils
import base64

API_KEY = "8U1YqN7Gfx7HJwkL6HD9cBKx"

IMAGES_DIR = os.path.join(config.FGFI_DIR, "input")
JSON_DIR   = os.path.join(config.FGFI_DIR, "output")
OUTPUT_DIR = os.path.join(config.IHS_DIR , "output")
NOBG_DIR   = os.path.join(OUTPUT_DIR     , "nobg")
DEBUG_DIR  = os.path.join(config.IHS_DIR , "debug")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
if not os.path.exists(NOBG_DIR):
    os.makedirs(NOBG_DIR)

def removebg(image):
    response = requests.post(
        'https://api.remove.bg/v1.0/removebg',
        files={'image_file': utils.image_to_bytes(image)},
        data={'size': 'regular'},
        headers={'X-Api-Key': API_KEY},
    )

    if response.status_code == requests.codes.ok:
        return io.BytesIO(response.content).getvalue()
    else:
        print("Error:", response.status_code, response.text)

if __name__ == "__main__":
    data = utils.from_json_file(os.path.join(JSON_DIR, "data.json"))
    input = utils.from_json_file(os.path.join(DEBUG_DIR, "input.json"))
    ngbg = []
    for face in input["faces"]:
        cropped = utils.get_cropped_image(data, face, config.FGFI_DIR)
        ngbg.append({
            "info": face, 
            "image_data": base64.b64encode(removebg(cropped, face)).decode("utf-8")
        })
    utils.save_to_json_file(os.path.join(OUTPUT_DIR, "nobg.json"), json.dumps(ngbg))