"""
MIT License

Copyright (c) Research @ RedHunt Labs Pvt Ltd
Written by Owais Shaikh
Email: owais.shaikh@redhuntlabs.com | 0x4f@tuta.io

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

import pytesseract, re, json, nltk, itertools, spacy, difflib, math


def string_tokenizer(text):
    words_list = text.replace(" ", "\n").split("\n")

    return [element for element in words_list if len(element) >= 2]


def similarity(stringA, stringB):
    return (
        math.floor(
            difflib.SequenceMatcher(
                a=stringA.lower(),
                b=stringB.lower()
            )
            .ratio() * 100
        )
    )


def get_regexes():
    with open('definitions.json') as json_file:
        return json.load(json_file)


def email_pii(text, rules):
    email_rules = rules["Email"]["regex"]
    email_addresses = re.findall(email_rules, text)
    email_addresses = list(set(filter(None, email_addresses)))
    return email_addresses


def phone_pii(text, rules):
    phone_rules = rules["Phone Number"]["regex"]
    phone_numbers = re.findall(phone_rules, text)
    phone_numbers = list(itertools.chain(*phone_numbers))
    phone_numbers = list(set(filter(None, phone_numbers)))
    return phone_numbers


def id_card_numbers_pii(text, rules):
    results = []

    # Clear all non-regional regexes
    regional_regexes = {}
    for key in rules.keys():
        region = rules[key]["region"]
        if region is not None:
            regional_regexes[key] = rules[key]

    # Grab regexes from objects
    for key in regional_regexes:
        region = rules[key]["region"]
        rule = rules[key]["regex"]

        try:
            match = re.findall(rule, text)
        except Exception:
            match = []

        if match:
            result = {'identifier_class': key, 'result': list(set(match))}
            results.append(result)

    return results


def read_pdf(pdf):
    return "".join(
        str(pytesseract.image_to_string(page, config='--psm 12'))
        for page in pdf
    )


# python -m spacy download en_core_web_sm
def regional_pii(text):
    import locationtagger
    try:
        place_entity = locationtagger.find_locations(text=text)
    except LookupError:
        nltk.downloader.download('punkt')
        nltk.download('averaged_perceptron_tagger')
        nltk.download('maxent_ne_chunker')
        nltk.download('words')
        place_entity = locationtagger.find_locations(text=text)

    return (
        place_entity.address_strings
        + place_entity.regions
        + place_entity.countries
    )


def keywords_classify_pii(rules, intelligible_text_list):
    keys = rules.keys()

    scores = {}

    for key in keys:
        scores[key] = 0
        keywords = rules[key]["keywords"]
        if keywords != None:
            # Compare each word in intelligible list with each word in keywords list 
            count = 0
            for intelligible_text_word in intelligible_text_list:
                for keywords_word in keywords:
                    if similarity(intelligible_text_word, keywords_word) > 75:
                        count += 1

                scores[key] = count

    return scores
