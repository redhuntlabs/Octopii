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

import requests, xmltodict, json, requests, cv2, urllib, http, traceback, os
from skimage import io
import numpy as np
from urllib.request import Request, urlopen, re
from bs4 import BeautifulSoup

def make_get_request(url):
    response = requests.get(url)
    return (response.content).decode("utf-8")

def list_s3_files(s3_location):
    file_path_list = []
    xml = (make_get_request(s3_location))
    s3_listing = xmltodict.parse(xml)
    s3_content_metadata = s3_listing["ListBucketResult"]["Contents"]
    for index, metadata in enumerate(s3_content_metadata):
        file_path = s3_content_metadata[index]['Key']
        file_path_list.append(s3_location + file_path)
    
    return file_path_list

def open_image(url):
    image = None
    try:
        request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urlopen(request).read()
        arr = np.asarray(bytearray(response), dtype=np.uint8)
        image = cv2.imdecode(arr, -1)

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
