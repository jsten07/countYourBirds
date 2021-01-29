import requests
import json
import base64
import yaml

# links: 
# sensebox forum: https://forum.sensebox.de/
# opensensemap: https://opensensemap.org/ 
# api documentation: https://docs.opensensemap.org/ 

# hint: If you want to try out new request, reproduce them on opensensemap and look in the browser console/ network analysis

# initialize variables 
senseboxAlreadyThere = False


# Read config.yaml file
with open("private/config.yaml", 'r') as stream:
    yamlData = yaml.safe_load(stream)

email = yamlData["sensebox"]["account"]["email"]
password = yamlData["sensebox"]["account"]["password"]
senseboxName = yamlData["sensebox"]["senseboxName"]
lat = yamlData["sensebox"]["coordinates"]["latitude"]
lng = yamlData["sensebox"]["coordinates"]["longitude"]



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





# Here the opensensemap is requested for all CountYourBirds senseboxes (so for all senseboxes with grouptag "CountYourBirds")
# This way it can be decided if the sensebox defined by the user in the config.yaml (variable "senseboxName") still needs to be created or not. 
# Is it still needed to create, later on there is the corresponding sensebox posted, if not and the sensebox is already there, 
# the corresponding senseboxId and sensorId are requested to be able to update the picture and the sensor value 
urlGetAllSenseboxes = 'https://api.opensensemap.org/boxes?grouptag=CountYourBirds'

requestGetAllSenseboxes = requests.get(urlGetAllSenseboxes)

responseGetAllSenseboxes = requestGetAllSenseboxes.text
responseGetAllSenseboxesParsed = json.loads(responseGetAllSenseboxes)

# for all received senseboxes is proofed if it is the sensebox defined by the user in the config.yaml 
# if it is the case the variable "senseboxAlreadyThere" is set to True so that its later on clear, that there is no need to create it again 
# Correspondingly senseboxId and sensorId are requested 
for x in responseGetAllSenseboxesParsed:
    if x['name'] == senseboxName:
        senseboxAlreadyThere = True
        
        senseboxId = x['_id']

        sensors = x['sensors']
        for y in sensors: 
            if y['title'] == 'Number of Counted Birds':
                senseboxSensorIdNumberOfCountedBirds = y['_id']
    else: 
        senseboxAlreadyThere = False 




# post a sensebox if the one mentioned in the config.yaml is not already there 
if senseboxAlreadyThere == False: 

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
    print(requestPostSensebox.text)





# send value to sensebox sensor
# Need to adapt senseboxId, senseboxSensorIdNumberOfCountedBirds in the config.yaml and value for corresponding sensebox and sensor 
if senseboxAlreadyThere == True: 
    value = '15'

    headersSendSensorValue = {'content-type': 'application/json',
               'Authorization': '946cd581ab67db398e9b8bc5f58b1f1dcde13465eb52a409c6b154ebc35ad77e'}
    urlSensorValueSensebox = 'https://api.opensensemap.org/boxes/' + senseboxId + '/data'

    dataValue = [{"sensor": senseboxSensorIdNumberOfCountedBirds, "value": value}]

    requestSensorValueSensebox = requests.post(urlSensorValueSensebox, json=dataValue, headers=headersSendSensorValue)
    print(requestSensorValueSensebox.status_code)
    print(requestSensorValueSensebox.text)





# update the sensebox with a picture
if senseboxAlreadyThere == True: 
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