# countYourBirds
This is an application to automatically recognize birds, specify the species, count and save pictures of them, only by use of one camera and a Raspberry Pi. The images and recorded values are made available online on https://opensensemap.org/. 

By using [Motion](https://pypi.org/project/motion/), movements are detected and corresponding images are captured. Afterwards, an object detection by [TensorFlow Lite](https://www.tensorflow.org/lite) is used to check if birds are present on the image. If birds are present in the images, the images are examined with another tensorflow lite model and an attempt is made to identify the species to which the bird belongs. Accordingly, the images on which birds were detected are stored and the detected birds are counted, also separated by species. The images and values are then automatically made available on [openSenseMap](https://opensensemap.org/) and can be retrieved at any time. 

The software is provided in relation to Citizien Science in such a way that citizens with a camera, a Raspberry Pi and the instructions available here can also use the application. It is convenient to install it together with a bird feeder. 

Instructions and all other information can be found in the [wiki](https://github.com/jsten07/countYourBirds/wiki).  

This is software that was developed as part of the study project "Image Recognition for Citizen Science" in the winterterm 2020/21 at [ifgi](https://www.uni-muenster.de/Geoinformatics/en/index.html) at the [University of Münster](https://www.uni-muenster.de/en/). 



