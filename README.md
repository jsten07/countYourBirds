# countYourBirds


## Image recognition live

First installation like described here: https://tutorials-raspberrypi.de/raspberry-pi-objekterkennung-mittels-tensorflow-und-kamera/

With this model: https://tfhub.dev/tensorflow/lite-model/ssd_mobilenet_v1/1/metadata/1?lite-format=tflite

Steps to activate, when you have already created the environment like in the description:
```shell
$ source tflite1-env/bin/activate
$ cd tflite1
$ python3 TFLite_detection_webcam.py --modeldir=Sample_TF_Lite_Model
```

## Run image recognition file
1. Steps to activate, when you have already created the environment like in the description:
```shell
$ source tflite1-env/bin/activate
$ cd tflite1
$ python3 TFLite_detection_webcam.py --modeldir=Sample_TF_Lite_Model
```
2. Run folowing command add the name of your image at name.jpg
```shell
$ python TFLite_detection_image.py --modeldir=Sample_TF_Lite_Model --image name.jpg
```
## Motion detection

Use this description to start https://www.bouvet.no/bouvet-deler/utbrudd/building-a-motion-activated-security-camera-with-the-raspberry-pi-zero

Have a look at motion.conf settings: e.g. decrease event_gap to 1 or 2
Possible configuration settings can be found here: https://motion-project.github.io/4.3.1/motion_config.html

start motion with 
- $ sudo motion -c /etc/motion/motion.conf
or 
- $ motion -c ~/.motion/motion.conf

stop with: 
- $ sudo service motion stop

see http://raspberrypi:8080/ for motion and camera control

settings:
- trigger image recognition script with e.g.
on_event_end  ..\script.py

## Next steps 
- get screenshots of several timesteps of the recorderd video to make them ready for classification 
- video/ screenshot gets classifed by tensorflow (in the motion.conf you can define a script which should be excecuted if there is a picture or video is saved)
- send an email or mattermost message if there was a bird recognition (https://www.bouvet.no/bouvet-deler/utbrudd/building-a-motion-activated-security-camera-with-the-raspberry-pi-zero)
- classify the birds by species 
- set up the raspberry pi at the balcony to produce first videos (using motion) + define settings for usable images 
- think about infrared recognition because by camera it is very energy consuming (https://randomnerdtutorials.com/raspberry-pi-motion-detector-photo-capture/)
