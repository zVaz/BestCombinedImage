from jsonExtractor import extractFacesProperties, getUpdatedGradesWeight, IMGG_DIR
import json
import utils
import os

# likeliness to grade weight dict   
strToGrade = { 'VERY_UNLIKELY' : 1,
                'UNLIKELY': 2,
                'POSSIBLE' : 3,
                'LIKELY' : 4,
                'VERY_LIKELY' : 5,
                'UNKOWN' : 0 }

# get updated faces properties and grade weight
faces = extractFacesProperties()
grades_weight = getUpdatedGradesWeight()

# initialize faceGrades
faceGrades = [[0]*len(faces) for i in range(len(faces[0]))]
# get attributes to iterate over
attributes = [a for a in dir(grades_weight) if not a.startswith('__')]

for image in range(len(faces)):
    for face in range(len(faces[0])):
        for attr in attributes:
            #print(getattr(faces[image][face], attr))
            #print(getattr(grades_weight, attr))
            faceAttrValue = getattr(faces[image][face], attr)
            # if attribute is a likeliness string, got to dict
            if type(faceAttrValue) is str:
                faceGrades[image][face] += strToGrade[faceAttrValue] * getattr(grades_weight, attr)
            else:
                faceGrades[image][face] += faceAttrValue * getattr(grades_weight, attr)

    print(faceGrades[image].index(max(faceGrades[image])))

# test
#faceGrades[1][1] = 100

# index for the base image
best_image_index = 0
# hold which face number of which person will be cropped into the base image
faces_to_swap = [] # row num =  face index, column num = group index

for i, grade in enumerate(faceGrades, 0):
    faces_to_swap.append({
            "group_index": i,
            "group_face_index": [row[i] for row in faceGrades].index(max([row[i] for row in faceGrades]))
    })

utils.save_to_json_file(os.path.join(IMGG_DIR, "input.json"), 
                        json.dumps( {
                                       "image_index": best_image_index,
                                       "faces": faces_to_swap
                                     }))


print("log")