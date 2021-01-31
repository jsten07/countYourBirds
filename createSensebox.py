import yaml
import os
import requests
import json


    

# Read config.yaml file
with open("/home/pi/tflite1/config.yaml", 'r') as stream:
    yamlData = yaml.safe_load(stream)

email = yamlData["sensebox"]["account"]["email"]
password = yamlData["sensebox"]["account"]["password"]
senseboxName = yamlData["sensebox"]["senseboxName"]
lat = yamlData["sensebox"]["coordinates"]["latitude"]
lng = yamlData["sensebox"]["coordinates"]["longitude"]
senseboxId = yamlData["sensebox"]["id"]

path = yamlData["folderPath"]

print(senseboxId)

# post a sensebox if the one mentioned in the config.yaml is not already there 
if senseboxId == "notSet":
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
    
    with open("/home/pi/tflite1/config.yaml") as stream:
        yamlData = yaml.safe_load(stream)
        
        yamlData["sensebox"]["id"] = senseboxId
        yamlData["sensebox"]["sensors"]["all"] = sensorId
        
        with open("/home/pi/tflite1/config.yaml", "w") as stream:
            yaml.dump(yamlData, stream)
        
        
    
    
    
