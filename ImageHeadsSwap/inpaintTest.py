import os
import numpy as np
import matplotlib.pyplot as plt

from skimage import data, io, color
from skimage.restoration import inpaint
from skimage.transform import rescale
from skimage.filters import threshold_otsu

RESULT_DIR   = "./result/"
if not os.path.exists(os.path.dirname(RESULT_DIR)):
    os.makedirs(os.path.dirname(RESULT_DIR))

a = io.imread('input.png')
image_orig = rescale(a, 1.0 / 4.0, anti_aliasing=False)

b = io.imread('mask.png')
mask = color.rgb2gray(rescale(b, 1.0 / 4.0, anti_aliasing=False))
thresh = threshold_otsu(mask)
binary = mask > thresh

# Defect image over the same region in each color channel
image_defect = image_orig.copy()
for layer in range(image_defect.shape[-1]):
    image_defect[np.where(binary)] = 0

image_result = inpaint.inpaint_biharmonic(image_defect, binary,
                                          multichannel=True)
image_result = rescale(image_result, 4.0, anti_aliasing=False)

io.imsave(os.path.join(RESULT_DIR, "image_orig.png"), a)
io.imsave(os.path.join(RESULT_DIR, "image_defect.png"), image_defect)
io.imsave(os.path.join(RESULT_DIR, "image_result.png"), image_result)

