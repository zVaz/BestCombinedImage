from sightengine.client import SightengineClient
from os.path import isfile, join, dirname
import sys    
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config

INPUT_DIR   = os.path.join(config.FGFI_DIR, "input")
OUTPUT_DIR   = os.path.join(config.FGFI_DIR, "output")

client = SightengineClient('793513700', '7zu2UXtkSFT68Cimrjy2')

def set_image_properties(image):
     return client.check('properties').set_file(image)
