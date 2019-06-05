import requests
import io, os ,sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config
import utils

RESULT_DIR = os.path.join(config.IHS_DIR, "result")

a = requests.post(url="https://inf.ngc.nvidia.com/v1/partialconv/inpainting", 
              files={
                  "original-image-file": open(os.path.join(RESULT_DIR, '5.jpg'), 'rb'), 
                  "masked-image-file": open(os.path.join(RESULT_DIR, 'mask_0 copy 3.png'), 'rb')
              })
print(a.text)