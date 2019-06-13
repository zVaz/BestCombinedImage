from jsonExtractor import extractFacesProperties, getUpdatedGradesWeight

strToGrade = { 'VERY_UNLIKELY' : 1,
                'UNLIKELY': 2,
                'POSSIBLE' : 3,
                'LIKELY' : 4,
                'VERY_LIKELY' : 5,
                'UNKOWN' : 0 }

faces = extractFacesProperties()
grades_weight = getUpdatedGradesWeight()

faceGrades = [[0]*len(faces) for i in range(len(faces[0]))]
attributes = [a for a in dir(grades_weight) if not a.startswith('__')]

for image in range(len(faces)):
    for face in range(len(faces[0])):
        for attr in attributes:
            #print(getattr(faces[image][face], attr))
            #print(getattr(grades_weight, attr))
            faceAttrValue = getattr(faces[image][face], attr)
            if type(faceAttrValue) is str:
                faceGrades[image][face] += strToGrade[faceAttrValue] * getattr(grades_weight, attr)
            else:
                faceGrades[image][face] += faceAttrValue * getattr(grades_weight, attr)

print("log")