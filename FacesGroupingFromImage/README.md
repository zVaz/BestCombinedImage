# **Faces Grouping From Image**
## **API Access**
### Google [Guide](https://cloud.google.com/vision/docs/quickstart-client-libraries)
1. Select or create a GCP project. [here](https://console.cloud.google.com/cloud-resource-manager?_ga=2.215698846.-822335999.1544290095)
2. Make sure that billing is enabled for your project. [here](https://cloud.google.com/billing/docs/how-to/modify-project)
3. Enable the Cloud Vision API. [here](https://console.cloud.google.com/flows/enableapi?apiid=vision-json.googleapis.com&_ga=2.105122826.-822335999.1544290095)
4. Set up authentication:
   1. In the GCP Console, go to the Create service account key page. [here](https://console.cloud.google.com/apis/credentials/serviceaccountkey?_ga=2.52249888.-822335999.1544290095)
   2. From the Service account drop-down list, select New service account.
   3. In the Service account name field, enter a name .
   4. From the Role drop-down list, select Project > Owner.
   5. Click Create. A JSON file that contains your key downloads to your computer.

### Amazon [Guide](https://docs.aws.amazon.com/rekognition/latest/dg/setting-up.html)
1. Create an AWS Account [here](https://aws.amazon.com/)
2. Create Group with policy `AmazonRekognitionFullAccess` [here](https://console.aws.amazon.com/iam/home#/groups)
3. Create an IAM User with `Programmatic access` and the group you have created [here](https://console.aws.amazon.com/iam/home#/users)
4. Copy the IAM User AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY


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

## **Environment Variables**

### Linux\macOS

Add the lines below

```
export AWS_ACCESS_KEY_ID="ACCESS KEY"
export AWS_SECRET_ACCESS_KEY="SECRET KEY"
export GOOGLE_APPLICATION_CREDENTIALS="PATH TO JSON FILE"
```

#### Linux
> ```nano ~/.bashrc```  
  ```source ~/.bashrc```

#### macOS
> ```nano ~/.bash_profile```  
  ```source ~/.bash_profile```

### Windwos
> Follow the [guide](http://www.forbeslindesay.co.uk/post/42833119552/permanently-set-environment-variables-on-windows) to add the variables below

```
Name: AWS_ACCESS_KEY_ID                   Value: "ACCESS KEY"
Name: AWS_SECRET_ACCESS_KEY               Value: "KEY"
Name: GOOGLE_APPLICATION_CREDENTIALS_PATH Value: "PATH TO JSON FILE"
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
