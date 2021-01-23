import requests
import json
import base64

# links: 
# sensebox forum: https://forum.sensebox.de/
# opensensemap: https://opensensemap.org/ 
# api documentation: https://docs.opensensemap.org/ 

# hint: If you want to try out new request, reproduce them on opensensemap and look in the browser console/ network analysis



# get sensebox
# Need to adapt senseboxIdGetSensebox
senseboxIdGetSensebox = '600c06299610e6001bd7a99e'
urlGetSensebox = 'https://api.opensensemap.org/boxes/' + senseboxIdGetSensebox + '?format=geojson'

#requestGetSensebox = requests.get(urlGetSensebox)
#print(requestGetSensebox.text)



# login to sensebox
# Needed for connection to accounts and for requests like post sensebox or update sensebox 
# Needed for requests like send sensor value  only if authentification needed is true 
headersLoginSensebox = {'content-type': 'application/json'}

urlLogin = 'https://api.opensensemap.org/users/sign-in'

paramsLogin = {'email': 'birdscounting@gmail.com', 'password': 'countingBirds'}

requestLogin = requests.post(urlLogin, params=paramsLogin, headers=headersLoginSensebox)
responseLogin = requestLogin.text
responseLoginParsed = json.loads(responseLogin)
jwtToken = responseLoginParsed['token']  # JWT = json web token




# post a sensebox
headersPostSensebox = {'content-type': 'application/json',
           'Authorization': 'Bearer ' + jwtToken}

name = 'CountYourBirdsRaesfeld'
exposure = 'outdoor'
lat = '51.76787'
lng = '6.772776'
icon = 'osem-signal'

dataPostSensebox = {"name": name, "exposure": exposure, "location": [lng, lat], "sensors": [
    {"icon": icon, "title": "Number of Counted Birds", "unit": "Birds"}]}

urlPostSensebox = 'https://api.opensensemap.org/boxes'

#requestPostSensebox = requests.post(urlPostSensebox, json = dataPostSensebox, headers = headersPostSensebox)
#print(requestPostSensebox.status_code)
#print(requestPostSensebox.text)





# send value to sensebox sensor
# Need to adapt senseboxId, sensorId and value for corresponding sensebox and sensor 
senseboxId = '600c0c3c9610e6001bda7df3'
sensorId = '600c0c3c9610e6001bda7df4'
value = '14'

headersSendSensorValue = {'content-type': 'application/json',
           'Authorization': '946cd581ab67db398e9b8bc5f58b1f1dcde13465eb52a409c6b154ebc35ad77e'}
urlSensorValueSensebox = 'https://api.opensensemap.org/boxes/' + senseboxId + '/data'

dataValue = [{"sensor": sensorId, "value": value}]

#requestSensorValueSensebox = requests.post(urlSensorValueSensebox, json=dataValue, headers=headersSendSensorValue)
#print(requestSensorValueSensebox.status_code)
#print(requestSensorValueSensebox.text)



# udate the sensebox with a picture
# need to adapt senseboxId
senseboxId = '600c0c3c9610e6001bda7df3'
headersUpdateSensebox={'content-type': 'application/json',
           'Authorization': 'Bearer ' + jwtToken}
description = 'The here shown values are collected by a Raspberry Pi. Each time a bird is recognized by the Raspberry Pi the here shown image gets updated, and the counter increases correspondingly. Further information about the system you can find by the following link:'
weblink = 'https://github.com/jsten07/countYourBirds'

# encoding of the image 
imageEncoded = base64.b64encode(open("opensensemapAPITestBird.jpeg", "rb").read())
imageEncodedString = imageEncoded.decode()
imageEncodedStringDataUri = 'data:image/jpeg;base64,' + imageEncodedString

urlUpdateSensebox = 'https://api.opensensemap.org/boxes/' + senseboxId

dataUpdateSensebox = {"description": description,"weblink": weblink, "image": imageEncodedStringDataUri}

#requestUpdateSensebox = requests.put(urlUpdateSensebox, json = dataUpdateSensebox, headers=headersUpdateSensebox)
#print(requestUpdateSensebox.status_code)
#print(requestUpdateSensebox.text)
