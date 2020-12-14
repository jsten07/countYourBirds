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

## Motion detection

Use this description to start https://www.bouvet.no/bouvet-deler/utbrudd/building-a-motion-activated-security-camera-with-the-raspberry-pi-zero

Have a look at motion.conf settings: e.g. decrease event_gap to 1 or 2

start motion with 
- $ sudo motion -c /etc/motion/motion.conf

stop with: 
- $ sudo service motion stop

## Next steps 

- get screenshots of several timesteps of the recorderd video to make them ready for classification 
- video/ screenshot gets classifed by tensorflow 
- python API for using mattermost 
- set up the raspberry pi at the balcony to produce first videos (using motion)
- send an email or mattermost message if there was a bird recognition
