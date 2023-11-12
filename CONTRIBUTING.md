Thank you for volunteering to contribute to Octopii. Make sure you are respectful of others and follow GitHub's [code of conduct](https://docs.github.com/en/site-policy/github-terms/github-community-code-of-conduct) when you try to contact someone, raise an issue or comment on this project. 

Open-source projects like these thrive on community support. Since Octopii relies heavily on preset definitions, contributions are much appreciated. Here's how to contribute:

### 1. Forking

Fork the official repository at https://github.com/redhuntlabs/octopii.git

### 2. Understanding

The `definitions.json` file consists of keywords to search for during an OCR scan, as well as other miscellaneous information such as country of origin, regular expressions etc.

An item in this file looks as follows:

```
"<pii class name>" : {
      "regex" : "<a regular expression or null>",
      "region" : <the country this PII originates from or null>,
      "keywords" : [
         "<keyword 1>",
         "<keyword 2>",
         ...
      ]
   },
```

### 3. Updating definitions

Keep the following rules in mind when writing your own definitions:

- PII class: The PII class name must contain the simple, common name of the document. For example, the Indian Government issued ID card is known as "Aadhaar", so that must be the PII class.
- Regex: The regex must be as precise as possible and must only exist if the ID card's identifier has an obvious pattern. For example, an Indian Permanent Account Number (PAN) card always has five Latin characters, followed by four numbers and a final Latin character (XXXXX0000X). Thus, a good regex can be used here. Please be extra careful with this step so as to avoid false positives. You may set this to `null` if you wish.
- Country of origin: Keep this as simple as possible and use common, shortened names. For example, "India" instead of "Republic of India". If you'd like to denote a province/state/subdivision, use the PII class field instead of this field. You may set this to `null` if you wish.
- Keywords: This is a list of prominent words in the Latin script, appearing in the document that can be picked up during OCR checks. Make sure these words are very specific to the document. Avoid using common words such as "the" or "of". For example, Indian Aadhaar cards have the words "Aadhaar", "Unique Identification" and "India" in English. These are good, unique words that generally don't appear in other documents.

### 4. Pull request

Submit a pull request and we'll pick it up and merge it if the changes look good.

For any queries, feel free to contact the developers and maintainers of this project