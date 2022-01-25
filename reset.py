from datetime import date
import cv2
import numpy as np
import os
import glob
import pickle


import yaml





from opensensemapAPI import *


def load_obj(name):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)
    
def save_obj(obj, name):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
        

    
    
# Read config.yaml file
with open("config.yaml", 'r') as stream:
    yamlData = yaml.safe_load(stream)

path = yamlData["folderPath"]
update = yamlData["sensebox"]["updateeveryhour"]
email = yamlData["sensebox"]["account"]["email"]
password = yamlData["sensebox"]["account"]["password"]
senseboxId =  yamlData["sensebox"]["id"]
# sensorId = yamlData["sensebox"]["sensors"]["all"]

PATH_TO_IMAGES = os.path.join(path,"imagesLastHour")
images = glob.glob(PATH_TO_IMAGES + '/*')
images.sort(key= os.path.getmtime)
image = ""


try:
    images = images[-4:]
    
except:
    images = images

imagesData = []
    # Loop over every image and perform detection
for image_path in images:

    # Load image and resize to expected shape [1xHxWx3]
    image = cv2.imread(image_path)
    imagesData.append(image)


print(images)
if len(imagesData) >= 4:
    
            image1=imagesData[3]
            image2=imagesData[2]
            image3=imagesData[1]
            image4=imagesData[0]

            # make all the images of same size 
            #so we will use resize functio

            # Now how we will attach image with other image
            # we will create a horizontal stack of images
            # then we will add it to the vertical stack
            # let the horizontal pair be (image1,image2)
            # and (image3,image4)
            # we will use numpy stack function
            Horizontal1=np.hstack([image1,image2])
            Horizontal2=np.hstack([image3,image4])
            print("yes")

            # Now the horizontal attachment is done
            # noe vertical attachment
            Vertical_attachment=np.vstack([Horizontal1,Horizontal2])
            size=(image1.shape[1], image.shape[0])
            image = cv2.resize(Vertical_attachment, size, interpolation=cv2.INTER_LINEAR)
            status = cv2.imwrite(os.path.join(path, "opensensemapImage.jpg"), image)
elif len(imagesData) >= 1:
   status = cv2.imwrite(os.path.join(path,"opensensemapImage.jpg"), imagesData[0])
   
token = login(email, password)
spec_file=load_obj("species")
for species in spec_file:
    sensorId= ""
    print(species)
    if  not (species in yamlData["sensebox"]["sensors"]):
        sensorId = createSensor(species, senseboxId, token)
    else:
        sensorId = yamlData["sensebox"]["sensors"][species]
    value = spec_file[species]
    updateSensor(sensorId, senseboxId, value, token)
    
    
if spec_file["all"] > 0:
        
    updateImage(senseboxId,image, token, update)
    
    
save_obj({"all" : 0}, "species")

now = datetime.now()
d = now.strftime("%d/%m/%Y, %H:%M")

history_file = load_obj("speciesHistory")
history_file[d] = spec_file
save_obj(history_file, "speciesHistory")
    

    
   
   


            
            
            


            
            
            
            