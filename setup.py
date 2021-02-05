import os
from crontab import CronTab
import yaml
import pickle
from opensensemapAPI import createSensebox

# Read config.yaml file
with open("config.yaml", 'r') as stream:
    yamlData = yaml.safe_load(stream)

path = yamlData["folderPath"]
environmentPath = yamlData["environmentPath"]
update = yamlData["sensebox"]["updateeveryhour"]
# Read config.yaml file
with open("config.yaml", 'r') as stream:
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
    createSensebox(email, password, lat, lng)



with open('species.pkl', 'wb') as f:
    pickle.dump({"all" : 0}, f, pickle.HIGHEST_PROTOCOL)

with open('speciesHistory.pkl', 'wb') as f:
    pickle.dump({}, f, pickle.HIGHEST_PROTOCOL)
    
    
os.makedirs("imagesLastHour", exist_ok=True)
os.makedirs("processed",  exist_ok=True)


cron = CronTab(user = True)

job= cron.new(command = "cd " + path + " && " +  environmentPath + "/bin/python "+ " reset.py")

if update < 1 :
    minutes = 60 * update
    print(minutes)
    job.every(minutes).minutes()
else:
    hour  = int(update)
    job.every(hour).hours()
    


#cron.write()
