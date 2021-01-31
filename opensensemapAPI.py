import requests
import json
import base64
import yaml
import os
from datetime import datetime

directory = "/home/pi/tflite1/"

# links: 
# sensebox forum: https://forum.sensebox.de/
# opensensemap: https://opensensemap.org/ 
# api documentation: https://docs.opensensemap.org/ 

# hint: If you want to try out new request, reproduce them on opensensemap and look in the browser console/ network analysis

# initialize variables 

senseboxAlreadyThere = False

# Read config.yaml file
with open(directory + "config.yaml", 'r') as stream:
    yamlData = yaml.safe_load(stream)

email = yamlData["sensebox"]["account"]["email"]
password = yamlData["sensebox"]["account"]["password"]
senseboxName = yamlData["sensebox"]["senseboxName"]
lat = yamlData["sensebox"]["coordinates"]["latitude"]
lng = yamlData["sensebox"]["coordinates"]["longitude"]
senseboxId =  yamlData["sensebox"]["id"]
sensorId = yamlData["sensebox"]["sensors"]["all"]

path = yamlData["folderPath"]

path1= os.path.join(path, "birds.txt")
path2= os.path.join(path, "birdsHistory.txt")
path3= os.path.join(path, "opensensemapImage.jpg")

if senseboxId != "notSet":
    senseboxAlreadyThere = True
else:
    print("Please run the setup.py skript before")

# login to sensebox
# Needed for connection to accounts and for requests like post sensebox or update sensebox 
# Needed for requests like send sensor value  only if authentification needed is true 
headersLoginSensebox = {'content-type': 'application/json'}

urlLogin = 'https://api.opensensemap.org/users/sign-in'

paramsLogin = {'email': email, 'password': password}

requestLogin = requests.post(urlLogin, params=paramsLogin, headers=headersLoginSensebox)
responseLogin = requestLogin.text
responseLoginParsed = json.loads(responseLogin)
jwtToken = responseLoginParsed['token']  # JWT = json web token





# send value to sensebox sensor
# Need to adapt senseboxId, senseboxSensorIdNumberOfCountedBirds in the config.yaml and value for corresponding sensebox and sensor 
if senseboxAlreadyThere == True:
    file = open(path1, "r+")
    fl = file.readline()
    birds = int(fl)
    file.seek(0)
    file.write(str(0))
    file.truncate()
    file.close()
    now = datetime.now()
    d = now.strftime("%d/%m/%Y, %H:%M")

    f = open(path2, "a")
    f.write("\n" + d + ": " + fl)
    f.close()
    value = birds

    headersSendSensorValue = {'content-type': 'application/json',
               'Authorization': '946cd581ab67db398e9b8bc5f58b1f1dcde13465eb52a409c6b154ebc35ad77e'}
    urlSensorValueSensebox = 'https://api.opensensemap.org/boxes/' + senseboxId + '/data'

    dataValue = [{"sensor": sensorId, "value": value}]

    requestSensorValueSensebox = requests.post(urlSensorValueSensebox, json=dataValue, headers=headersSendSensorValue)
    print(requestSensorValueSensebox.status_code)
    print(requestSensorValueSensebox.text)





# update the sensebox with a picture
if senseboxAlreadyThere == True and value > 0: 
    headersUpdateSensebox={'content-type': 'application/json',
               'Authorization': 'Bearer ' + jwtToken}
    description = 'The here shown values are collected by a Raspberry Pi. Each time a bird is recognized by the Raspberry Pi the here shown image gets updated, and the counter increases correspondingly. Further information about the system you can find by the following link:'
    weblink = 'https://github.com/jsten07/countYourBirds'

    # encoding of the image 
    imageEncoded = base64.b64encode(open(path3, "rb").read())
    imageEncodedString = imageEncoded.decode()
    imageEncodedStringDataUri = 'data:image/jpeg;base64,' + imageEncodedString

    urlUpdateSensebox = 'https://api.opensensemap.org/boxes/' + senseboxId

    dataUpdateSensebox = {"description": description,"weblink": weblink, "image": imageEncodedStringDataUri}

    requestUpdateSensebox = requests.put(urlUpdateSensebox, json = dataUpdateSensebox, headers=headersUpdateSensebox)
    print(requestUpdateSensebox.status_code)
    print(requestUpdateSensebox.text)





# further code not needed at the moment: 

# get sensebox by Id 
# Need to adapt senseboxIdGetSensebox
# senseboxIdGetSensebox = '600c06299610e6001bd7a99e'
# urlGetSensebox = 'https://api.opensensemap.org/boxes/' + senseboxIdGetSensebox + '?format=geojson'
# requestGetSensebox = requests.get(urlGetSensebox)
# print(requestGetSensebox.text)