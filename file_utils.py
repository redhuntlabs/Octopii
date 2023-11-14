"""
MIT License

Copyright (c) Research @ RedHunt Labs Pvt Ltd
Written by Owais Shaikh
Email: owais.shaikh@redhuntlabs.com | me@0x4f.in

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

import requests, xmltodict, json, requests, cv2, urllib, http, traceback, os, textract, webhook, octopii
from skimage import io
import numpy as np
from urllib.request import Request, urlopen, re
from bs4 import BeautifulSoup
from pdf2image import convert_from_path
from PIL import Image

def truncate(local_location):
    characters_per_file = 1232500
    file_data = ""

    with open(local_location, 'r') as file: 
        file_data = file.read()
        file.close()
        
    truncated_data = file_data[0:characters_per_file]

    with open(local_location, 'w') as file:
        file.write(truncated_data)
        file.close()

def make_get_request(url):
    response = requests.get(url)
    return (response.content).decode("utf-8")

def list_s3_files(s3_location):
    if s3_location[-1] != '/':
        s3_location = s3_location + '/'

    file_path_list = []
    xml = (make_get_request(s3_location))
    s3_listing = xmltodict.parse(xml)
    s3_content_metadata = s3_listing["ListBucketResult"]["Contents"]
    for index, metadata in enumerate(s3_content_metadata):
        file_path = s3_content_metadata[index]['Key']
        file_path_list.append(s3_location + file_path)
    
    return file_path_list

def open_remote_file(url):
    image = None
    try:
        file_name = url.split('/')[-1]
        urllib.request.urlretrieve(url, "temp/"+file_name)

    except urllib.error.HTTPError:
        print("Couldn't access " + url)
        # traceback.print_exc()
        image = None
            
    except cv2.error:
        print("Error decoding image at " + url)
        image = None

    except http.client.IncompleteRead:
        print("Error reading image at " + url + ". Connection interrupted.")
        image = None

    return image

def list_directory_files(url):
    urls_list = []
    url = url.replace(" ","%20")
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urlopen(request).read()
    soup = BeautifulSoup(response, 'html.parser')
    a_tags = (soup.find_all('a'))
    for a_tag in a_tags:
        file_name = ""
        try: 
            file_name = re.compile('(?<=<a href=\")(.+)(?=\">)').findall(str(a_tag))[0]
            if "?C=" in file_name or len(file_name) <= 3:
                raise TypeError

        except TypeError: # fallback
            file_name = a_tag.extract().get_text()

        url_new = url  + file_name
        url_new = url_new.replace(" ","%20")
        urls_list.append (url_new)
    
    return urls_list

def list_local_files(local_path):
    files_list = []
    for root, subdirectories, files in os.walk(local_path):
        for file in files:
            relative_path = (os.path.join(root, file))
            files_list.append(relative_path)

    return files_list

def is_pdf(file_path):
    try:
        convert_from_path(file_path, 100)
        return True
    except:
        return False

def is_image(file_path):
    try:
        i=Image.open(file_path)
        return True
    except:
        return False

def append_to_output_file(data, file_name):
    try:
        loaded_json = []
        try: 
            with open(file_name, 'r+') as read_file:    
                loaded_json = json.loads(read_file.read())
        except: # No file
            print ("\nCreating new file named \'" + file_name + "\' and writing to it.")
        with open(file_name, 'w') as write_file:
            loaded_json.append(data)
            write_file.write(json.dumps(loaded_json, indent=4))
            
    except:
        traceback.print_exc()
        print ("Couldn't write to "+ file_name +". Please check if the path is correct and try again.")