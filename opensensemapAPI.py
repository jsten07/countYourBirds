import requests
import json
import base64
import yaml
import os
from datetime import datetime

# links: 
# sensebox forum: https://forum.sensebox.de/
# opensensemap: https://opensensemap.org/ 
# api documentation: https://docs.opensensemap.org/ 

# hint: If you want to try out new request, reproduce them on opensensemap and look in the browser console/ network analysis


# Function to login on opensensemap
# Needed for connection to accounts and for requests like post sensebox or update sensebox 
# Needed for requests like send sensor value  only if authentification needed is true 
def login(email, password):
    headersLoginSensebox = {'content-type': 'application/json'}

    urlLogin = 'https://api.opensensemap.org/users/sign-in'

    paramsLogin = {'email': email, 'password': password}

    requestLogin = requests.post(urlLogin, params=paramsLogin, headers=headersLoginSensebox)
    responseLogin = requestLogin.text
    responseLoginParsed = json.loads(responseLogin)
    jwtToken = responseLoginParsed['token']  # JWT = json web token
    return(jwtToken)




# Function to update a sensor of a sensebox with a new value 
def updateSensor(sensorId, senseboxId, value ,jwtToken):

    headersSendSensorValue = {'content-type': 'application/json',
               'Authorization': 'Bearer ' + jwtToken}
    urlSensorValueSensebox = 'https://api.opensensemap.org/boxes/' + senseboxId + '/data'

    dataValue = [{"sensor": sensorId, "value": value}]

    requestSensorValueSensebox = requests.post(urlSensorValueSensebox, json=dataValue, headers=headersSendSensorValue)
    print(requestSensorValueSensebox.status_code)
    print(requestSensorValueSensebox.text)




# Function to update a sensebox with a new image 
def updateImage(senseboxId, image, jwtToken, update):
    headersUpdateSensebox={'content-type': 'application/json',
               'Authorization': 'Bearer ' + jwtToken}
       description = 'Raspberry Pi automatically recognizing birds. Every ' + str(update) + ' h the above-shown collage and the sensors (birds in total and separated by species with the Latin name) are updated with the recognized birds in the last ' + str(update) + ' h. Further information can be found here:'

    weblink = 'https://github.com/jsten07/countYourBirds'

    # encoding of the image 
    imageEncoded = base64.b64encode(open('opensensemapImage.jpg', "rb").read())
    imageEncodedString = imageEncoded.decode()
    imageEncodedStringDataUri = 'data:image/jpeg;base64,' + imageEncodedString

    urlUpdateSensebox = 'https://api.opensensemap.org/boxes/' + senseboxId

    dataUpdateSensebox = {"description": description,"weblink": weblink, "image": imageEncodedStringDataUri}

    requestUpdateSensebox = requests.put(urlUpdateSensebox, json = dataUpdateSensebox, headers=headersUpdateSensebox)
    print(requestUpdateSensebox.status_code)
    print(requestUpdateSensebox.text)




# Function to create a new sensebox
def createSensebox(email, password, lat, lng):
    
    headersLoginSensebox = {'content-type': 'application/json'}

    urlLogin = 'https://api.opensensemap.org/users/sign-in'

    paramsLogin = {'email': email, 'password': password}

    requestLogin = requests.post(urlLogin, params=paramsLogin, headers=headersLoginSensebox)
    responseLogin = requestLogin.text
    responseLoginParsed = json.loads(responseLogin)
    jwtToken = responseLoginParsed['token']  # JWT = json web token


    headersPostSensebox = {'content-type': 'application/json',
               'Authorization': 'Bearer ' + jwtToken}

    # lat, lng are already defined at the top, by the config.yaml
    name = senseboxName
    exposure = 'outdoor'
    grouptag = 'CountYourBirds'
    icon = 'osem-signal'

    dataPostSensebox = {"name": name, "exposure": exposure, "location": [lng, lat], "grouptag": grouptag, "sensors": [
        {"icon": icon, "title": "Number of Counted Birds", "unit": "Birds"}]}

    urlPostSensebox = 'https://api.opensensemap.org/boxes'

    requestPostSensebox = requests.post(urlPostSensebox, json = dataPostSensebox, headers = headersPostSensebox)
    print(requestPostSensebox.status_code)
    resultJSON = json.loads(requestPostSensebox.text)
    print(resultJSON)
    senseboxId = resultJSON["data"]["_id"]
    sensorId = resultJSON["data"]["sensors"][0]["_id"]
    print(senseboxId)
    
    with open("config.yaml") as stream:
        yamlData = yaml.safe_load(stream)
        
        yamlData["sensebox"]["id"] = senseboxId
        yamlData["sensebox"]["sensors"]["all"] = sensorId
        
        with open("config.yaml", "w") as stream:
            yaml.dump(yamlData, stream)




# Function to create a new sensor for a sensebox          
def createSensor(species, senseboxId, jwtToken):  

    sensorName = "Number of Counted Birds – " + species
    icon = 'osem-signal'

    headersUpdateSensebox={'content-type': 'application/json',
           'Authorization': 'Bearer ' + jwtToken}

    urlUpdateSensebox = 'https://api.opensensemap.org/boxes/' + senseboxId

    dataPostNewSensor = {"sensors": [
        {"icon": icon, "title": sensorName, "unit": "Birds", "new": "true", "edited":"true"}]}

    requestUpdateSensebox = requests.put(urlUpdateSensebox, json = dataPostNewSensor, headers=headersUpdateSensebox)
    print(requestUpdateSensebox.status_code)
    print(requestUpdateSensebox.text)
    resultJSON = json.loads(requestUpdateSensebox.text)

    sensors = resultJSON["data"]["sensors"]
    sensorId = sensors[len(sensors) - 1]["_id"]
    print(senseboxId)
        
    with open("config.yaml") as stream:
        yamlData = yaml.safe_load(stream)
            
        yamlData["sensebox"]["sensors"][species] = sensorId
            
        with open("config.yaml", "w") as stream:
            yaml.dump(yamlData, stream)
            
    print(sensorId)
    return(sensorId)




# further code not needed at the moment: 

# get sensebox by Id 
# Need to adapt senseboxIdGetSensebox
# senseboxIdGetSensebox = '600c06299610e6001bd7a99e'
# urlGetSensebox = 'https://api.opensensemap.org/boxes/' + senseboxIdGetSensebox + '?format=geojson'
# requestGetSensebox = requests.get(urlGetSensebox)
# print(requestGetSensebox.text)