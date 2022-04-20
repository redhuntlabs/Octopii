"""
MIT License

Copyright (c) 2022 Owais Shaikh 
Research @ RedHunt Labs Pvt Ltd
Email: owais.shaikh@redhuntlabs.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


from enum import auto
import os, sys, json, traceback
from time import sleep
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from textwrap import indent
from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np
import pytesseract, cv2, math, re
from skimage.io import imread
from skimage.morphology import convex_hull_image
import matplotlib as plt
import file_utils
from urllib.parse import urlparse


model_file_name = 'models/keras_model.h5'
labels_file_name = 'models/labels.txt'
ocr_list_file_name = 'models/ocr_list.json'

# Create the array of the right shape to feed into the keras model
# The 'length' or number of images you can put into the array is
# determined by the first position in the shape tuple, in this case 1.
model = load_model(model_file_name)
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

def write_json(data, file_name):
    try:
        with open(file_name, 'w') as data_file:
            data_file.write(json.dumps(data))
            data_file.close()

        return True
    except:
        return False

def load_json(json_file, trimmed):
    with open(json_file) as data_file:
        data = json.load(data_file)
        if trimmed:
            # get rid of casing and spacing to make things easier
            original_keys = [key for key in [*data]]
            cleaned_keys = [key.lower().replace(' ', '') for key in [*data]]

            for index, key in enumerate (cleaned_keys):
                data[key] = data.pop(original_keys[index])

        return data

def get_labels(labels_file_name):
        labels = {}
        with open (labels_file_name, "r") as label:
            text = label.read()
            lines = text.split ("\n")
            for line in lines[0:-1]:
                    hold = line.split (" ", 1)
                    labels[hold[0]] = hold[1]

        return labels

def scan_for_text(image_path):
    image = None
    if "http" in image_path: image = file_utils.open_image(image_path)
    else: image = cv2.imread(image_path, 0)
    text = str(pytesseract.image_to_string(image, config = '--psm 12')).lower()
    return text

confidence_score = None
def classify_image(image_path):
    global confidence_score
    image = None
    if "http" in image_path: 
        cv2_image = cv2.cvtColor(file_utils.open_image(image_path), cv2.COLOR_BGR2RGB)
        image = Image.fromarray(cv2_image)
    else: 
        image = Image.open(image_path).convert('RGB')
    
    size = (224, 224) # resizing for faster scanning
    image = ImageOps.fit(image, size, Image.ANTIALIAS)
    image_array = np.asarray(image) #turn the image into a numpy array
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1 # Normalize the image
    data[0] = normalized_image_array # Load the image into the array
    
    # run the inference
    pred = model.predict(data)
    result = np.argmax(pred[0])
    converted_pred = str.split(np.array_str(pred[0]).replace("[", "").replace("]", ""))
    confidence_score = math.floor(max([float(score.split("e")[0])*10 for score in converted_pred])) # confidence in percentages of highest probability
    confidence_score = confidence_score
    
    labels = get_labels(labels_file_name)
    
    asset_type = labels[str(result)]

    return asset_type

def predict(image_path):
    global confidence_score
    pii_type = None
    country_of_origin = None

    ocr_list = load_json(ocr_list_file_name, trimmed=True)
    
    try: 
        # Step 1. OCR
        scanned_text = scan_for_text(image_path).lower()

        # Step 2. Image Classification
        pii_type = classify_image(image_path)
    
        # Step 3. Combining Steps 1 and 2
        found = False
        keywords = ocr_list[pii_type.lower().replace(" ", "")]["keywords"]
        for keyword in keywords:
            country_of_origin = ocr_list[pii_type.lower().replace(" ", "")]["country"]
            keyword = keyword.lower().replace(' ', "")
            if scanned_text.lower().find(keyword) >= 0:
                confidence_score = 100
                found = True

        # Step 4. Run plain OCR if Image Classification + OCR doesn't work
        if found == False:
            trimmed_ocr_list = load_json(ocr_list_file_name, trimmed = False)
            for asset_class, data in trimmed_ocr_list.items():
                for keyword in data["keywords"]:
                    if scanned_text.lower().find(keyword) >= 0:
                        country_of_origin = data["country"]
                        pii_type = asset_class
                        confidence_score = 50
                        found = True

    except cv2.error:
        print("Couldn't read image: " + str (image_path))
        # traceback.print_exc()

    except (TypeError, ValueError):
        print("Not a valid image format: " + str (image_path))
        traceback.print_exc()

    except (KeyError):
        pass
        print("No text found in: " + str (image_path))
        # traceback.print_exc()

    except (Exception):
        print("Unknown error while reading: " + str (image_path))
        traceback.print_exc()
    
    return (pii_type, country_of_origin, confidence_score)

if __name__ in '__main__':
    files = []
    items = []
    location = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

    if "http" in location:
        try:
            files = file_utils.list_s3_files(location)
        except:
            try:
                files = file_utils.list_directory_files(location)
            except:
                print ("This URL is not a valid S3 or has no directory listing enabled. Try running piiscan locally on the server.")
                sys.exit(-1)

    else:
        files = file_utils.list_local_files(location)

    for file_path in files:
        try:
            prediction = predict(file_path)
            asset_type = prediction[0]
            country_of_origin = prediction[1]
            confidence = prediction[2]
            file_name = os.path.basename(urlparse(file_path).path)
            extension = str(os.path.splitext(file_path)[1][1:])
            path = str(file_path)

            dictionary = {
                "asset_type": asset_type, 
                "country_of_origin": country_of_origin, 
                "confidence": confidence, 
                "file_name" : file_name, 
                "extension": extension, 
                "path": path
            }
        
            items.append(dictionary)

        except: pass

    data = json.dumps(items, indent = 4)
    print (data)
    # write_json (items, "output.json")

    sys.exit(0)
            