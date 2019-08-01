from PIL import Image, ImageDraw
import numpy as np
import math

neighboors_offsets = [
    (-1, -1), (0, -1), (1, -1),
    (-1,  0),          (1,  0),
    (-1,  1), (0,  1), (1,  1)
]

neighboors_offsets2 = [
              (0, -1), 
    (-1,  0),          (1,  0),
              (0,  1)
]

def add_pixels(pixel1, pixel2):
    return (pixel1[0] + pixel2[0], pixel1[1] + pixel2[1])

def get_neighboors(pixel, width, height, offsets = neighboors_offsets):
    neighboors = []

    for neighboor_offsets in offsets:
        neighboor = add_pixels(pixel, neighboor_offsets)
        if 0 <= neighboor[0] < width and 0 <= neighboor[1] < height:
            neighboors.append(neighboor)

    return neighboors


def get_first_border_pixel(mask_pixdata, width, height):
    # find the first pixel of border
    for y in range(height):
        for x in range(width):
            if mask_pixdata[x, y] == 255:
                return (x, y)
    return None

def is_border_pixel(mask_pixdata, neighboor, width, height):
    # Checks that the pixel is white
    if mask_pixdata[neighboor[0], neighboor[1]] == 255:
        # Checks if havr black neighboor in offsets neighboors_offsets2
        if any(mask_pixdata[suspected_neighboor[0], 
                            suspected_neighboor[1]] == 0 for suspected_neighboor in get_neighboors(neighboor, width, height, neighboors_offsets2)):
            return True
    return False
def get_border_of_mask(mask):
    mask_pixdata = mask.load()
    width, height = mask.size
    border = []
    border_queue = []

    first_border_pixel = get_first_border_pixel(mask_pixdata, width, height)
    if first_border_pixel != None:
        border_queue.append(first_border_pixel)

    while len(border_queue) != 0:
        current = border_queue.pop(0)
        neighboors = get_neighboors(current, width, height)
        
        for neighboor in neighboors:
            # Checks that not already in border
            if not neighboor in border:
                if is_border_pixel(mask_pixdata, neighboor, width, height):
                    border_queue.append(neighboor)
        border.append(current)

    #img = Image.new('L', (width,height), color = 0)
    #pixdata = img.load()
    #for pixel in border:
    #   pixdata[pixel[0], pixel[1]] = 255
    #img.show()

    return border

class BorderDistance(object):
    def __init__(self, disntance = 0):
        self._distance = disntance
        self._is_visited = False
    
    def is_visited(self):
        return self._is_visited

    def set_visited(self, distance):
        self._is_visited = True
        self._distance = distance
    
    def get_distance(self):
        return self._distance
                
def get_disntances_from_border(mask, border):
    mask_pixdata = mask.load()
    width, height = mask.size

    disntances = np.array([ [ BorderDistance() for _ in range(width)] for _ in range(height) ], dtype=object)

    for pixel in border:
        disntances[pixel[0], pixel[1]].set_visited(0)

    pixel_queue = border.copy()

    disntances_dict = {}
    
    while len(pixel_queue) != 0:
        current = pixel_queue.pop(0)
        neighboors = get_neighboors(current, width, height, neighboors_offsets)

        for neighboor in neighboors:
            if mask_pixdata[neighboor[0], neighboor[1]] == 255:
                if not disntances[neighboor[0], neighboor[1]].is_visited():
                    disntances[neighboor[0], neighboor[1]].set_visited(disntances[current[0], current[1]].get_distance() + 1)
                    pixel_queue.append(neighboor)
        disntances_dict.setdefault(disntances[current[0], current[1]].get_distance(), []).append(current)

    #img = Image.new('L', (width,height), color = 0)
    #pixdata = img.load()
    #max_distance = len(disntances_dict)
    #distance_value = 255.0 / max_distance
    #for distance, pixels in disntances_dict.items():
    #    for pixel in pixels:
    #        pixdata[pixel[0], pixel[1]] = 255 - math.floor(distance * distance_value)
    #img.show()

    return disntances_dict
        


if __name__ == "__main__":
    mask = Image.open(open(r"./result/mask_1.png", "rb"))
    border = get_border_of_mask(mask)
    disntances_dict = get_disntances_from_border(mask, border)