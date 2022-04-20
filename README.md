# Piiscan

Piiscan is an AI-powered Personal Identifiable Information (PII) scanner that can look for Government IDs, passports, photos and signatures in a directory.

## Working
Piiscan uses Tesseract's Optical Character Recognition (OCR) and Keras' Convolutional Neural Networks (CNN) models to detect various forms of personal identifiable information that may be leaked on a publicly facing location. This is done via:

1. Importing and cleaning image(s)

The image is imported via OpenCV and is cleaned, deskewed and rotated for scanning.

2. Performing image classification

The image is scanned for features such as an ISO/IEC 7810 card specification, colors, location of text, photos, holograms etc. This is done by passing it anf comparing it against a trained model.

3. Optical Character Recognition (OCR)

As a final verification method, images are scanned for certain strings to verify the accuracy of the model.

The accuracy of the scan can determined via the confidence scores in output. If all the mentioned conditions are met, a score of 100.0 is returned. 

To train the model, data can also be fed into the `model_generator.py` script, and the newly improved h5 file can be used.

## Usage
```
python3 piiscan.py <location to scan> <additional flags>
```
1. Install all dependencies via `pip install -r requirements.txt`.
2. To run piiscan, type `python3 piiscan.py <location name>`, for example `python3 piiscan.py pii_list/`

Piiscan currently supports local directories, s3 directories and open directory listing. 

### Example
```
owais@artemis ~ $ python3 piiscan.py pii_list

Not a valid image format: pii_list/aadhaar/aadhaar-8.gif

[
    {
        "asset_type": "Bank",
        "confidence": 100.0,
        "file_name": "passbook",
        "extension": "jpeg",
        "path": "pii_list/bank/passbook.jpeg"
    },
    {
        "asset_type": "Photo",
        "confidence": 99.98,
        "file_name": "IMG-20200331-WA0037",
        "extension": "jpg",
        "path": "pii_list/photos/IMG-20200331-WA0037.jpg"
    },
    {
        "asset_type": "PAN",
        "confidence": 100.0,
        "file_name": "pan-7",
        "extension": "jpg",
        "path": "pii_list/pan/pan-7.jpg"
    },
    {
        "asset_type": "Aadhaar",
        "confidence": 97.31,
        "file_name": "aadhaar-14",
        "extension": "jpg",
        "path": "pii_list/aadhaar/aadhaar-14.jpg"
    }
]
```

## Contributing
Open-source projects like these thrive on community support. Since piiscan relies heavily on machine learning and optical character recognition,  contributions are much appreciated. Here's how to contribute:

1. Fork the official repository at https://github.com/redhuntlabs/piiscan
2. There are 3 files in the `models/` directory. 
    - The `keras_models.h5` file is the Keras h5 model that can be obtained from Google's Teachable Machine or via Keras in Python.
    - The `labels.txt` file contains the list of labels corresponding to the index that the model returns. 
    - The `ocr_list.json` file consists of keywords to search for during an OCR scan, as well as other miscellaneous information such as country of origin, regular expressions etc.

### Generating models via Teachable Machine
Since our current dataset is quite small, we could benefit from a large Keras model of international PII for this project. If you do not have expertise in Keras, Google provides an extremely easy to use model generator called the Teachable Machine. To use it:
- Visit https://teachablemachine.withgoogle.com/train and select 'Image Project' → 'Standard Image Model'.
- A few classes are visible. Rename the class to an asset type ypu'd like to upload, such as "German Passport" or "California Driver License".
- Add images by clicking the 'Upload' button and upload some image assets. **Note: images have to be square**

*Tip: segregate your image assets into folders with the folder name being the same as the class name. You can then drag and drop a folder into the upload dialog.*

**NOTE: Only upload the same as the class name, for example, German Passport class must have German Passport pictures. Uploading the wrong data to the wrong class will confuse the machine learning algorithms.** 
- Click '+ Add a class' at the bottom of the page to add more classes with data and repeat. You can make the classes more specific, such as "Goa Driver License Old Format".
- Verify the classes and images one last time. Once you're ready, click on the 'Train Model' button. You can increase the epoch size (such as 5000) to improve model accuracy.
- To test, you can test the model by clicking the Input dropdown and selecting 'File', then uploading a sample image.
- Once you're ready, click the 'Export Model' button. In the dialog that pops up, select the 'Tensorflow' tab (not Tensorflow.js) and select the 'Keras' radio button, then click 'Download my model' to export the newly generated model. Extract the downloaded zip file and paste the `keras_model.h5` file and `labels.txt` file into the `models/` directory in piiscan.

The images used for the model above are not visible to us since they're in a proprietary format. You can use both dummy and actual PII. Make sure they are square-ish in image size. 

### Updating OCR list
Once you generate models using Teachable Machine, you can improve piiscan's accuracy via OCR. To do this:
- Open the existing `ocr_list.json` file. Create a JSONObject with the key having the same name as the asset class. **NOTE: The key name must be exactly the same as the asset class name from Teachable Machine.**
- For the `keywords`, use as many unique terms from your asset as possible, such as "Income Tax Department". Store them in a JSONArray.
- *(Advanced)* you can also add regexes for things like ID numbers and MRZ on passports if they are unique enough. Use https://regex101.com to test your regexes before adding them.
- Save/overwrite the existing `ocr_list.json` file.

3. You can replace each file you modify in the `models/` directory after you create or edit them via the above methods.
4. Submit a pull request from your forked repo and we'll pick it up and add it to our current model.

**Note:** Please take the following steps to ensure quality
- Make sure the model returns extremely accurate results by testing it locally first. 
- Use proper text casing for label names in both the Keras model and `ocr_list.json`. 
- Make sure all JSON is valid with appropriate character escapes with no duplicate keys, regexes or keywords. 
- For country names, please use the ISO 3166-1 alpha-2 code of the country.

<!--
### Flags

- #### (Work in progress) `--validate-aadhaar`
Uses UIDAI APIs to validate any Aadhaar cards found and checks if they actually exist. Helps avoid false positives.

- #### (Work in progress) `--model=<h5 file>`
Use a custom model with the script.

- #### (Work in progress) `--retrain`
Classifies scanned images into folders and retrains the model on them. Asks user if a document is of a certain type via (Y/n) or if a new data class must be created. 
-->

---

## Credits

- [BeautifulSoup](https://beautiful-soup-4.readthedocs.io/en/latest/)
- [Tesseract](https://github.com/madmaze/pytesseract)
- [Keras](https://keras.io/)
- [SciKit](https://scikit-learn.org/)
- Python Image Library
- [Spaces - DigitalOcean](https://www.digitalocean.com/products/spaces)
- [Teachable Macine - Google](https://teachablemachine.withgoogle.com/) 

## License

[MIT License](LICENSE)

(c) Copyright 2022 RedHunt Labs Private Limited

Author: Owais Shaikh