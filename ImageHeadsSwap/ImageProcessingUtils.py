from PIL import Image, ImageDraw

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
        current = border_queue.pop()
        neighboors = get_neighboors(current, width, height)
        
        for neighboor in neighboors:
            # Checks that not already in border
            if not neighboor in border:
                if is_border_pixel(mask_pixdata, neighboor, width, height):
                    border_queue.append(neighboor)
        border.append(current)

    img = Image.new('L', (width,height), color = 0)
    pixdata = img.load()

    for pixel in border:
        pixdata[pixel[0], pixel[1]] = 255
    img.show()
    return border

                

if __name__ == "__main__":
    mask = Image.open(open(r"./result/mask_1.png", "rb"))
    border = get_border_of_mask(mask)
