import argparse
import cv2
import importlib.util
import numpy as np
import time
import pickle

def load_labels(filename):
  with open(filename, 'r') as f:
    return [line.strip() for line in f.readlines()]



def save_obj(obj, name):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)

def count_spec(species):
    spec_file = load_obj('species')
    if species in spec_file:
        spec_file[species] += 1
    else:
        spec_file[species] = 1
        
    save_obj(spec_file, 'species')
    
    print(spec_file)


def add_spec(spec_dict):
    spec_file = load_obj('species')
    spec_file = {k: spec_dict.get(k, 0) + spec_file.get(k, 0) for k in set(spec_dict) | set(spec_file)}
    save_obj(spec_file, 'species')
    
    print(spec_file)
    return(spec_file)
   


pkg = importlib.util.find_spec('tflite_runtime')
if pkg:
    from tflite_runtime.interpreter import Interpreter
else:
    from tensorflow.lite.python.interpreter import Interpreter

interpreter = Interpreter(model_path="models/bird_classification/classify.tflite")
labels = load_labels("models/bird_classification/probability-labels-en.txt")

interpreter.allocate_tensors()

# Get model details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

floating_model = (input_details[0]['dtype'] == np.float32)

input_mean = 127.5
input_std = 127.5

# image = cv2.imread(image_path)
# test_im = cv2.imread("/home/pi/motion/saved/test_4.jpg")

def classify(image_array):
    # cv2.imwrite("/home/pi/motion/saved/test.jpg", image_array)
    
    #cv2.imshow("bird", image_array)
    #cv2.waitKey(2000)
    try:
            image_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
            imH, imW, _ = image_array.shape
            image_resized = cv2.resize(image_rgb, (width, height))
            input_data = np.expand_dims(image_resized, axis=0)
            
            if floating_model:
                input_data = (np.float32(input_data) - input_mean) / input_std

            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()

            output_data = interpreter.get_tensor(output_details[0]['index'])
            results = np.squeeze(output_data)
            
            # print(results)

            top_k = results.argsort()[-5:][::-1]
            bird_name = ""
            for i in top_k:
                if floating_model:
                    print('{:08.6f}: {}'.format(float(results[i]), labels[i]))
                    if float(results[i]) > 0.5:
                        bird_name = labels[i]
                else:
                    print('{:08.6f}: {}'.format(float(results[i] / 255.0), labels[i]))
                    if float(results[i] / 255.0) > 0.5:
                        bird_name = labels[i]
            # print(bird_name)
            return bird_name
    except:
            return ""

#classify(test_im)
