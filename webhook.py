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

import requests
import json

def push_data(data: str, url: str):
    headers = {'Content-type': 'application/json'}
    
    if "discord" in url:
        payload = {"content": data}
    else:
        payload = {"text": data}
    
    try:
        req = requests.post(
            url,
            headers=headers,
            json=payload,  # Use the json parameter to send JSON data
            timeout=7
        )

        req.raise_for_status()  # Raise an HTTPError for bad responses

        print('Scan results sent to webhook.')
    except requests.exceptions.RequestException as e:
        print(f'Couldn\'t send scan results to webhook. Reason: {e}')
