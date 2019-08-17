from FacesGroupingFromImage.FacesGroupingFromImage import main as fgfi_main
from ImageGrading.gradingSystem import main as imgg_main
from ImageHeadsSwap.ImageHeadsSwap import main as ihs_main
import time

if __name__ == "__main__":
    start = time.time()
    print("Start - Face detection and recognition")
    fgfi_main()
    print("End - Face detection and recognition")
    print("Start - Image and faces scoring")
    imgg_main()
    print("End - Image and faces scoring")
    print("Start - Head swap")
    ihs_main()
    print("End - Head swap")
    print("Time of processing: {}".format(time.time() - start))