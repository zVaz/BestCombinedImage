from PIL import Image, ImageDraw
import numpy as np
import math
from collections import OrderedDict
import time
from dataclasses import dataclass
import cProfile

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


def get_first_border_pixel(mask, mask_pixdata, width, height):
    a = np.array(mask)
    rows, cols = np.where(a > 128)
    if len(rows) > 0 and len(cols) > 0:
        return (int(cols[0]), int(rows[0]))
    return None

def is_border_pixel(mask_pixdata, neighboor, width, height):
    # Checks that the pixel is white
    if mask_pixdata[neighboor[0], neighboor[1]] > 128:
        # Checks if havr black neighboor in offsets neighboors_offsets2
        if any(mask_pixdata[suspected_neighboor[0], 
                            suspected_neighboor[1]] <= 128 for suspected_neighboor in get_neighboors(neighboor, width, height)):
            return True
    return False

def get_border_of_mask(mask):
    mask_pixdata = mask.load()
    width, height = mask.size
    border = []
    border_queue = []

    first_border_pixel = get_first_border_pixel(mask, mask_pixdata, width, height)

    if first_border_pixel != None:
        border_queue.append(first_border_pixel)

    while len(border_queue) != 0:
        current = border_queue.pop(0)
        neighboors = get_neighboors(current, width, height)
        
        for neighboor in neighboors:
            # Checks that not already in border
            if not neighboor in border:
                if neighboor not in border and neighboor not in border_queue and is_border_pixel(mask_pixdata, neighboor, width, height):
                    border_queue.append(neighboor)
        border.append(current)

    #img = Image.new('L', (width,height), color = 0)
    #pixdata = img.load()
    #for pixel in border:
    #   pixdata[pixel[0], pixel[1]] = 255
    #img.show()

    return border

class BorderDistance(object):
    __slots__ = ["_distance", "_is_visited"]
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
                
def get_disntances_from_border(mask, border, radius):
    mask_pixdata = mask.load()
    width, height = mask.size

    start = time.time()
    disntances = np.full(shape=(width, height),fill_value=None, dtype=object)
    print(time.time() - start)

    for pixel in border:
        disntances[pixel[0], pixel[1]] = BorderDistance()
        disntances[pixel[0], pixel[1]].set_visited(0)

    pixel_queue = border.copy()

    disntances_dict = OrderedDict()
    
    while len(pixel_queue) != 0:
        current = pixel_queue.pop(0)
        current_distance = disntances[current[0], current[1]].get_distance()
        neighboors = get_neighboors(current, width, height, neighboors_offsets)
        for neighboor in neighboors:
            if mask_pixdata[neighboor[0], neighboor[1]] <= 128:
                if disntances[neighboor[0], neighboor[1]] == None:
                    disntances[neighboor[0], neighboor[1]] = BorderDistance()
                if not disntances[neighboor[0], neighboor[1]].is_visited():
                    disntances[neighboor[0], neighboor[1]].set_visited(current_distance - 1)
                    pixel_queue.append(neighboor)
        if current_distance == -radius:
            break
        disntances_dict.setdefault(current_distance, set()).add(current)
    disntances_dict = OrderedDict(reversed(list(disntances_dict.items())))
    pixel_queue = border.copy()
    start = time.time()
    while len(pixel_queue) != 0:
        current = pixel_queue.pop(0)
        current_distance = disntances[current[0], current[1]].get_distance()
        neighboors = get_neighboors(current, width, height, neighboors_offsets)
        for neighboor in neighboors:
            if mask_pixdata[neighboor[0], neighboor[1]] > 128:
                if disntances[neighboor[0], neighboor[1]] == None:
                    disntances[neighboor[0], neighboor[1]] = BorderDistance()
                if not disntances[neighboor[0], neighboor[1]].is_visited():
                    disntances[neighboor[0], neighboor[1]].set_visited(current_distance + 1)
                    pixel_queue.append(neighboor)
        disntances_dict.setdefault(current_distance, set()).add(current)
    print(time.time() - start)

    #start = time.time()
    #img = Image.new('L', (width,height), color = 0)
    #pixdata = img.load()
    #max_distance = len(disntances_dict)
    #distance_value = 255.0 / max_distance
    #for distance, pixels in disntances_dict.items():
    #    for pixel in pixels:
    #        pixdata[pixel[0], pixel[1]] = 255 - math.floor(distance * distance_value)
    #print(time.time() - start)
    #img.show()

    return disntances_dict, disntances
        
def inpaint_image(img ,disntances_dict, disntances):
    ret = img.copy()
    img_pixdata = ret.load()
    width, height = img.size
    max_distance = len(disntances_dict)
    for disntance, disntance_list in disntances_dict.items():
        for coord in disntance_list:
            coord_dist = disntances[coord[0], coord[1]].get_distance()

            neighboors = get_neighboors(coord, width, height)

            max_cost = 0
            for neighboor in neighboors:
                border_distance = disntances[neighboor[0], neighboor[1]]
                neighboor_dist = 0 if border_distance == None else border_distance.get_distance()
                if neighboor_dist < coord_dist and neighboor_dist > max_cost:
                    max_cost = neighboor_dist
            max_cost += 1

            pixel_value = (0, 0, 0)
            total_cost = 0
            for neighboor in neighboors:
                border_distance = disntances[neighboor[0], neighboor[1]]
                neighboor_pixel_value = img_pixdata[neighboor[0], neighboor[1]]
                neighboor_dist = 0 if border_distance == None else border_distance.get_distance()
                if neighboor_dist < coord_dist:
                    total_cost += 1
                    #total_cost += max_cost - neighboor_dist
                    #neighboor_part = tuple(c for c in neighboor_pixel_value)
                    pixel_value = tuple(a + b for a, b in zip(neighboor_pixel_value, pixel_value))
                    #neighboor_part = tuple(c * (max_cost - neighboor_dist) for c in neighboor_pixel_value)
                    #pixel_value = tuple(a + b for a, b in zip(neighboor_part, pixel_value))

            #total_cost += max_cost - coord_dist
            #coord_part = tuple(c * (max_cost - coord_dist) for c in img_pixdata[coord[0], coord[1]])
            #pixel_value = tuple(a + b for a, b in zip(coord_part, pixel_value))
            if total_cost == 0:
                pixel_value = tuple(a + b for a, b in zip(img_pixdata[coord[0], coord[1]], pixel_value))
                pixel_value = tuple(int(c / (total_cost + 1)) for c in pixel_value)
            else:
                pixel_value = tuple(int(c / (total_cost)) for c in pixel_value)
            img_pixdata[coord[0], coord[1]] = pixel_value
    #ret.show()
    return ret

def mask_from_disntances_dict(mask, disntances_dict, data):
    chin_tip = next(filter(lambda landmark: landmark["type"] == "CHIN_GNATHION", data["landmarks"]), None)
    chin_tip = (int(chin_tip["position"]["x"]), int(chin_tip["position"]["y"]))
    print(chin_tip)
    width, height = mask.size
    new_mask = Image.new('L', (width,height), color = 0)
    pixdata = new_mask.load()
    for distances_list in disntances_dict.values():
        for pixel in distances_list:
            if pixel[1] < (chin_tip[1] + 4) // 3:
                pixdata[pixel[0], pixel[1]] = 255
    return new_mask

def inpaint(img, mask, data, radius):
    print("Start inpaint")
    radius = math.floor(radius / 1.5)
    width, height = mask.size
    small_img = img.resize((img.size[0] // 3, img.size[1] // 3), Image.ANTIALIAS)

    small_mask = mask.resize((mask.size[0] // 3, mask.size[1] // 3), Image.ANTIALIAS)
    border = get_border_of_mask(small_mask)
    disntances_dict, disntances = get_disntances_from_border(small_mask, border, radius)
    ret = inpaint_image(small_img, disntances_dict, disntances)
    inpainted_mask_image = mask_from_disntances_dict(small_mask, disntances_dict, data)
    inpainted_mask_image = inpainted_mask_image.resize(mask.size, Image.ANTIALIAS)
    ret = ret.resize(img.size, Image.ANTIALIAS)

    ret = Image.composite(ret, img, inpainted_mask_image.convert("L"))
    print("End inpaint")
    return ret, inpainted_mask_image

if __name__ == "__main__":
    start = time.time()
    mask = Image.open(open(r"./result/mask_0.png", "rb")).convert("L")
    img = Image.open(open(r"../FacesGroupingFromImage/input/a.jpeg", "rb"))
    inp, inpainted_mask_image = inpaint(img, mask, 8)
    #cProfile.run('inpaint(img, mask)')
    inpainted_mask_image.show()
    inp.show()
    print(time.time() - start)
