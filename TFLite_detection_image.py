######## Webcam Object Detection Using Tensorflow-trained Classifier #########
#
# Author of original script: Evan Juras
# Date: 9/28/19
# Description: 
# This program uses a TensorFlow Lite object detection model to perform object 
# detection on an image or a folder full of images. It draws boxes and scores 
# around the objects of interest in each image.
#
# This code is based off the TensorFlow Lite image classification example at:
# https://github.com/tensorflow/tensorflow/blob/master/tensorflow/lite/examples/python/label_image.py
#
# I added my own method of drawing boxes and labels using OpenCV.

# Import packages
import os
import argparse
import cv2
import numpy as np
import sys
import glob
import importlib.util
import email, smtplib, ssl


from TFLite_classify_birds import classify, add_spec

import yaml

# Read config.yaml file
with open("config.yaml", 'r') as stream:
    yamlData = yaml.safe_load(stream)

path = yamlData["folderPath"]

emailWanted = yamlData["email"]["wanted"]

hours = yamlData["sensebox"]["updateeveryhour"]
threshold = yamlData["detection"]["threshold"]

if emailWanted: 

    from email import encoders
    from email.mime.base import MIMEBase
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.image import MIMEImage
    
    imagesWanted = yamlData["email"]["images"]

    subject = "Bird Summary"
    sender_email = yamlData["email"]["sender"]["email"]
    receiver_email = [yamlData["email"]["receiver"]["email"]]
    password= yamlData["email"]["sender"]["password"]

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = yamlData["email"]["receiver"]["email"]
    message["Subject"] = subject
    #message["Bcc"] = receiver_email  # Recommended for mass emails


    # Log in to server using secure context and send email
    context = ssl.create_default_context()


def overlapping1D(line1, line2):
    return ((line1[1] >= line2[0]) and (line2[1] >= line1[0]))

def overlapping2D(box1, box2):
    return (overlapping1D(box1[0], box2[0]) and overlapping1D(box1[1], box2[1]) )

def count_spec(species, spec_file):
    if not ('all' in spec_file):
        spec_file['all'] = 0
    spec_file['all'] += 1
    if species in spec_file:
        spec_file[species] += 1
    else:
        if species != '':
            spec_file[species] = 1
    return spec_file

# Log in to server using secure context and send email
context = ssl.create_default_context()


#context = ssl.create_default_context()

# Define and parse input arguments
parser = argparse.ArgumentParser()
parser.add_argument('--modeldir', help='Folder the .tflite file is located in',
                    required=True)
parser.add_argument('--graph', help='Name of the .tflite file, if different than detect.tflite',
                    default='detect.tflite')
parser.add_argument('--labels', help='Name of the labelmap file, if different than labelmap.txt',
                    default='labelmap.txt')
parser.add_argument('--threshold', help='Minimum confidence threshold for displaying detected objects',
                    default=threshold)
parser.add_argument('--image', help='Name of the single image to perform detection on. To run detection on multiple images, use --imagedir',
                    default=None)
parser.add_argument('--imagedir', help='Name of the folder containing images to perform detection on. Folder must contain only images.',
                    default=None)
parser.add_argument('--edgetpu', help='Use Coral Edge TPU Accelerator to speed up detection',
                    action='store_true')

args = parser.parse_args()

MODEL_NAME = args.modeldir
GRAPH_NAME = args.graph
LABELMAP_NAME = args.labels
min_conf_threshold = float(args.threshold)
use_TPU = args.edgetpu

# Parse input image name and directory. 
IM_NAME = args.image
IM_DIR = args.imagedir

# If both an image AND a folder are specified, throw an error
if (IM_NAME and IM_DIR):
    print('Error! Please only use the --image argument or the --imagedir argument, not both. Issue "python TFLite_detection_image.py -h" for help.')
    sys.exit()

# If neither an image or a folder are specified, default to using 'test1.jpg' for image name
if (not IM_NAME and not IM_DIR):
    IM_NAME = 'test1.jpg'

# Import TensorFlow libraries
# If tflite_runtime is installed, import interpreter from tflite_runtime, else import from regular tensorflow
# If using Coral Edge TPU, import the load_delegate library
pkg = importlib.util.find_spec('tflite_runtime')
if pkg:
    from tflite_runtime.interpreter import Interpreter
    if use_TPU:
        from tflite_runtime.interpreter import load_delegate
else:
    from tensorflow.lite.python.interpreter import Interpreter
    if use_TPU:
        from tensorflow.lite.python.interpreter import load_delegate

# If using Edge TPU, assign filename for Edge TPU model
if use_TPU:
    # If user has specified the name of the .tflite file, use that name, otherwise use default 'edgetpu.tflite'
    if (GRAPH_NAME == 'detect.tflite'):
        GRAPH_NAME = 'edgetpu.tflite'


# Get path to current working directory
CWD_PATH = os.getcwd()
PATH_TO_IMAGES = ""

# Define path to images and grab all image filenames
if IM_DIR:
    PATH_TO_IMAGES = os.path.join(CWD_PATH,IM_DIR)
    images = glob.glob(PATH_TO_IMAGES + '/*')

elif IM_NAME:
    PATH_TO_IMAGES = os.path.join(CWD_PATH,IM_NAME)
    images = glob.glob(PATH_TO_IMAGES)

# Path to .tflite file, which contains the model that is used for object detection
PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,GRAPH_NAME)

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH,MODEL_NAME,LABELMAP_NAME)

# Load the label map
with open(PATH_TO_LABELS, 'r') as f:
    labels = [line.strip() for line in f.readlines()]

# Have to do a weird fix for label map if using the COCO "starter model" from
# https://www.tensorflow.org/lite/models/object_detection/overview
# First label is '???', which has to be removed.
if labels[0] == '???':
    del(labels[0])

# Load the Tensorflow Lite model.
# If using Edge TPU, use special load_delegate argument
if use_TPU:
    interpreter = Interpreter(model_path=PATH_TO_CKPT,
                              experimental_delegates=[load_delegate('libedgetpu.so.1.0')])
    print(PATH_TO_CKPT)
else:
    interpreter = Interpreter(model_path=PATH_TO_CKPT)

interpreter.allocate_tensors()

# Get model details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

floating_model = (input_details[0]['dtype'] == np.float32)

input_mean = 127.5
input_std = 127.5

birdInOne = False
birdImages=[]
birdCountAll={}
status = ""
filenameNew= ""


# Loop over every image and perform detection
for image_path in images:

    # Load image and resize to expected shape [1xHxWx3]
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    imH, imW, _ = image.shape 
    image_resized = cv2.resize(image_rgb, (width, height))
    input_data = np.expand_dims(image_resized, axis=0)
    birdDetected = False
    highestScore = 0
    # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
    if floating_model:
        input_data = (np.float32(input_data) - input_mean) / input_std

    # Perform the actual detection by running the model with the image as input
    interpreter.set_tensor(input_details[0]['index'],input_data)
    interpreter.invoke()

    # Retrieve detection results
    boxes = interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects
    classes = interpreter.get_tensor(output_details[1]['index'])[0] # Class index of detected objects
    scores = interpreter.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects
    #num = interpreter.get_tensor(output_details[3]['index'])[0]  # Total number of detected objects (inaccurate and not needed)
    birdCount={}
    birdBoxes=[]
    # Loop over all detections and draw detection box if confidence is above minimum threshold
    for i in range(len(scores)):
        if ((scores[i] > min_conf_threshold) and (scores[i] <= 1.0)):

            if(int(classes[i]) == 15):
                
                # Get bounding box coordinates and draw box
                # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
                ymin = int(max(1,(boxes[i][0] * imH)))
                xmin = int(max(1,(boxes[i][1] * imW)))
                ymax = int(min(imH,(boxes[i][2] * imH)))
                xmax = int(min(imW,(boxes[i][3] * imW)))
                
                ydif = int((ymax-ymin)/2)
                xdif = int((xmax-xmin)/2)
                
                # cv2.imshow('Object detector', image)
                im_crop = image.copy()[ymin-xdif:ymax+xdif, xmin-ydif:xmax+ydif]
                # cv2.imwrite("/home/pi/motion/saved/test" + str(i) + ".jpg", im_crop)
                # cv2.imshow('sample', image)
                species = classify(im_crop)
                print(species)
                
                cv2.rectangle(image, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)

                # Draw label
                object_name = labels[int(classes[i])] # Look up object name from "labels" array using class index
                label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'
                if species != "":
                    label = label + " (" + species + ")"
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
                label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
                cv2.rectangle(image, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
                cv2.putText(image, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text
                
                newBox = [[ymin, ymax], [xmin,xmax]]
                highestScore = max(highestScore, scores[i])
                doubleBox= False
                for boxes in birdBoxes:
                    if(overlapping2D):
                        doubleBox = True
                        print("Bird already counted")
                
                if(not doubleBox):
                    birdBoxes.append([[ymin, ymax], [xmin,xmax]])
                    birdCount = count_spec(species, birdCount)
                birdDetected = True
                birdInOne = True
                print("Bird detected")
                

    if sum(birdCountAll.values()) > sum(birdCount.values()):
        birdCountAll = birdCountAll
    else:
        birdCountAll = birdCount
        
                    #with smtplib.SMTP_SSL("smtp.gmail.com", port, context = context) as server:
                        #server.login

    # All the results have been drawn on the image, now display the image
    #cv2.imshow('Object detector', image)
    if(birdDetected == True):
        headTail =  os.path.split(image_path)
        
        filenameNew = "processed_" + headTail[1]
        IM_NAMEnew = os.path.join(headTail[0], filenameNew)
        status = cv2.imwrite(IM_NAMEnew, image)
        status = cv2.imwrite(os.path.join(path,"processed", filenameNew), image)
        data = {}
        data["score"] = highestScore
        data["image"] = IM_NAMEnew
        birdImages.append(data)
         # In same directory as script
             # Press any key to continue to next image, or press 'q' to quit
 
         
if(birdInOne):
        birds = add_spec(birdCountAll)
        birds = birds["all"]
        
        print(species)
        if species == "":
            spec_text = ""
        else:
            spec_text = " of species " + species
        text = MIMEText(str(birdCountAll["all"]) + " new Bird(s)" + spec_text + " detected.\nTotal birds detected in the last " + str(hours) + " hour(s): "+ str(birds))
        message.attach(text)
        print(status)
        sortedImages = sorted(birdImages, key = lambda x : x["score"], reverse = True)
        im_data = cv2.imread(sortedImages[0]["image"])
        status = cv2.imwrite(os.path.join(path,"imagesLastHour", filenameNew), im_data)
        print(sortedImages)
        if emailWanted:
            min1= min(3, birdCountAll["all"])
            for i in range(min1):
                im_data = open(sortedImages[i]["image"], "rb").read()
                headTail =  os.path.split(sortedImages[i]["image"])
                filenameNew = "processed_" + headTail[1]
                image = MIMEImage(im_data, name= filenameNew)
                message.attach(image)
                
        # read all the image
        # we are going to take 4 images only
        

        # Add attachment to message and convert message to string

            text = message.as_string()
            print("E-Mail send")
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, text)

        

f1 = open("hello.txt", "r+")
f1.seek(0)
f1.write("false")
f1.truncate()
f1.close()

for image_path in images:
    os.remove(image_path)
os.removedirs(PATH_TO_IMAGES)


# Clean up
cv2.destroyAllWindows()
