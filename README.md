# **BestCombinedImage**

## **Usage**
```git clone https://github.com/avivco94/BestCombinedImage.git```

## **Directories**
```
FacesGroupingFromImage (FGFI) - For faces grouping
ImageHeadsSwap         (IHS)  - For head swaping
ImageGrading           (IG)   - For grading photos and extracting the highest graded photo
```
## Shared Code
> Add those lines to accsess Shared Code
```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config
import utils
```

## **Json Structures**
### **FGFI** - data.json

```python
{
    "images": [
        {
            "path": path,
            "faces": [
                {
                    #Google Vision API response
                    ...
                }
            ]
        },
        ...
    ],
    "groups": [
        [ { "image": index, "face": index }, { "image": index, "face": index }, ... ],
        ...
    ]
}
```

### **IG** - to_replace.json
```python
{
    "image_index": index,
    "faces": [
        {
            "image_index": index, 
            "face_index": index
        },
        {
            "image_index": index, 
            "face_index": index
        },
        ...
    ]    
}
```

### **IHS** - nobg.json
```python
[
    {
        "info": {
            "image_index": index, 
            "face_index": index
        }, 
        "image_data": base64
    },
    {
        "info": {
            "image_index": index, 
            "face_index": index
        }, 
        "image_data": base64
    },
    ...
]
```