import os
import numpy as np
from skimage import data, io, color
from skimage.restoration import inpaint
from skimage.transform import rescale
from skimage.filters import threshold_otsu
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config
import utils

def inpaint_image(image, mask):
    image = np.array(image.copy())
    mask = np.array(mask.copy())
    image_orig = rescale(image, 1.0 / 4.0, anti_aliasing=False)
    mask = color.rgb2gray(rescale(mask, 1.0 / 4.0, anti_aliasing=False))
    thresh = threshold_otsu(mask)
    binary = mask > thresh
    image_defect = image_orig.copy()
    for layer in range(image_defect.shape[-1]):
        image_defect[np.where(binary)] = 0
    image_result = inpaint.inpaint_biharmonic(image_defect, binary,
                                            multichannel=True)
    image_result = rescale(image_result, 4.0, anti_aliasing=False)
    mask_result = rescale(mask, 4.0, anti_aliasing=False)

    return image_result, mask_result

RESULT_DIR = os.path.join(config.IHS_DIR, "result")

if not os.path.exists(os.path.dirname(RESULT_DIR)):
    os.makedirs(os.path.dirname(RESULT_DIR))

if __name__ == "__main__":
    image = io.imread(os.path.join(config.IHS_DIR, 'input.png'))
    mask = io.imread(os.path.join(config.IHS_DIR, 'mask.png'))

    image_result, mask = inpaint_image(image, mask)
    io.imsave(os.path.join(RESULT_DIR, "image_orig.png"), image)
    io.imsave(os.path.join(RESULT_DIR, "image_result.png"), image_result)

