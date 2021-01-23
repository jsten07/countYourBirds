from datetime import date


file = open("/home/pi/tflite1/birds.txt", "r+")
fl = file.readline()
birds = int(fl)
file.seek(0)
file.write(str(0))
file.truncate()
file.close()
today = date.today()
d = today.strftime("%d/%m/%Y")

f = open("/home/pi/tflite1/birdsHistory.txt", "a")
f.write("\n" + d + ": " + fl)
f.close()
