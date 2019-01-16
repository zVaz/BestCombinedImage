# **Faces Grouping From Image**
## **Virtualenv and Requirements**
> You can install the requirements.txt globally and ignore the virtualenv
### Linux\macOS
1. ```pip3 install virtualenv```
2. ```virtualenv project```
3. ```source project/bin/activate```
4. ```pip install -r requirements.txt```

### Windows
1. ```pip install virtualenv```
2. ```virtualenv project```
3. ```project\Scripts\activate```
4. ```pip install -r requirements.txt```

## **Profile Paths**
### Linux
> Add the lines below to ~/.profile
### macOS
> Add the lines below to ~/.bash_profile
### Windwos
> Follow the [guide](http://www.forbeslindesay.co.uk/post/42833119552/permanently-set-environment-variables-on-windows)
```
export AWS_ACCESS_KEY_ID="ACCESS KEY"
export AWS_SECRET_ACCESS_KEY="SECRET KEY"
export GOOGLE_APPLICATION_CREDENTIALS_PATH="PATH TO JSON FILE"
```

## **Paths**
```
./images/  - The images folder
./cropped/ - The cropped faces from the images (temporery until the faces grouping)
./groups/  - Contains directory for each group
```

## **Running The Project**
>  Virtualenv: ```source project/bin/activate```

```python FacesGroupingFromImage.py```
