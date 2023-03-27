import difflib, math, ast
from pdf2image import convert_from_path
import pytesseract, re, json, textract, sys, getopt, nltk, itertools

def string_tokenizer(text):
    final_word_list = []
    words_list = text.replace(" ", "\n").split("\n")
    
    for element in words_list: 
        if len(element) >= 2: 
            final_word_list.append(element)
    
    return final_word_list

def similarity(stringA, stringB):
    return (
        math.floor (
            difflib.SequenceMatcher (
                a=stringA.lower(), 
                b=stringB.lower()
            )
            .ratio() * 100
        )
    )

def get_regexes():
    with open('definitions.json') as json_file:
        _rules = json.load(json_file)
        return _rules

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
            regional_regexes[key]=rules[key]

    # Grab regexes from objects
    for key in regional_regexes.keys():
        region = rules[key]["region"]
        rule = rules[key]["regex"]
        
        try:
            match = re.findall(rule, text)
        except:
            match=[]

        if len(match) > 0:
            result = {'identifier_class':key, 'result': list(set(match))}
            results.append(result)

    return results

def read_pdf(pdf):
    pdf_contents=""
    for page in pdf:
        pdf_contents += str(pytesseract.image_to_string(page, config = '--psm 12'))

    return pdf_contents

# python -m spacy download en_core_web_sm
def regional_pii(text):
    import locationtagger
    try:
        place_entity = locationtagger.find_locations(text = text)
        return place_entity.address_strings + place_entity.regions + place_entity.countries
    except LookupError:
        nltk.downloader.download('punkt')
        nltk.download('averaged_perceptron_tagger')
        nltk.download('maxent_ne_chunker')
        nltk.download('words')
        place_entity = locationtagger.find_locations(text = text)
        return place_entity.address_strings + place_entity.regions + place_entity.countries

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
    