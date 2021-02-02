import os
from crontab import CronTab
import yaml
import pickle

# Read config.yaml file
with open("config.yaml", 'r') as stream:
    yamlData = yaml.safe_load(stream)

path = yamlData["folderPath"]
update = yamlData["sensebox"]["updateeveryhour"]

path1= os.path.join(path, "reset.py")
path2= os.path.join(path, "createSensebox.py")



f = open("birds.txt", "w+")
f.write("0")
f.close()


f = open("birdsHistory.txt", "w+")
f.write("History")
f.close()

with open('species.pkl', 'wb') as f:
    pickle.dump({}, f, pickle.HIGHEST_PROTOCOL)

os.makedirs("imagesLastHour", exist_ok=True)
os.makedirs("processed",  exist_ok=True)


cron = CronTab(user = True)

job= cron.new(command = "/home/pi/tflite1-env/bin/python " +path1)

if update < 1 :
    minutes = 60 * update
    print(minutes)
    job.every(minutes).minutes()
else:
    hour  = int(update)
    job.every(hour).hours()
    

os.system("/home/pi/tflite1-env/bin/python "+ path2)

cron.write()