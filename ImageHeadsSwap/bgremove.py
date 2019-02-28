# Requires "requests" to be installed (see python-requests.org)
import requests
import os

API_KEY = "8U1YqN7Gfx7HJwkL6HD9cBKx"

IMAGES_DIR = "./images/"
NOBG_DIR   = "./nobg/"

if not os.path.exists(os.path.dirname(IMAGES_DIR)):
    os.makedirs(os.path.dirname(IMAGES_DIR))
if not os.path.exists(os.path.dirname(NOBG_DIR)):
    os.makedirs(os.path.dirname(NOBG_DIR))

def removebg(images_dir, filename):
    image_path = os.path.join(images_dir,filename)
    response = requests.post(
        'https://api.remove.bg/v1.0/removebg',
        files={'image_file': open(image_path, 'rb')},
        data={'size': 'regular'},
        headers={'X-Api-Key': API_KEY},
    )

    if response.status_code == requests.codes.ok:
        with open(os.path.join(NOBG_DIR,filename), 'wb') as out:
            out.write(response.content)
    else:
        print("Error:", response.status_code, response.text)

if __name__ == "__main__":
    for filename in os.listdir(IMAGES_DIR):
        removebg(IMAGES_DIR,filename)