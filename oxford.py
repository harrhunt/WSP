# for more information on how to install requests# http://docs.python-requests.org/en/master/user/install/#install
import glob
import re
import time

import requests
import json
from os.path import exists
from credentials import OXFORD_APP_KEY, OXFORD_APP_ID


def get_all(word):
    path = f"data/words/{word.lower()}.json"
    if exists(path):
        print("Loaded from file")
        with open(path, "r") as file:
            data = json.load(file)
    else:
        url = f'https://od-api.oxforddictionaries.com/api/v2/entries/en-us/{word.lower()}?strictMatch=true'
        r = requests.get(url, headers={'app_id': OXFORD_APP_ID, 'app_key': OXFORD_APP_KEY})
        if r.status_code == 200:
            data = r.json()
            with open(path, "w") as file:
                json.dump(data, file)
        else:
            return r.status_code
    return data["results"]


def get_defs(word, subdefinitions=False):
    definitions = []
    results = get_all(word)
    if isinstance(results, int):
        return "404: word not found"
    for result in results:
        for lex in result["lexicalEntries"]:
            for entry in lex["entries"]:
                for sense in entry["senses"]:
                    for definition in sense["definitions"]:
                        definitions.append(definition)
                    if subdefinitions:
                        if "subsenses" in sense:
                            for subsense in sense["subsenses"]:
                                for subdefinition in subsense["definitions"]:
                                    definitions.append(subdefinition)
    return definitions


def save_words_not_found(wnf):
    with open("404.json", "w") as file:
        json.dump(wnf, file)


if __name__ == '__main__':
    with open("404.json", "r") as file:
        words_not_found = json.load(file)
    files = glob.glob("data/comparisons/*.json")
    for filename in files:
        name = re.split("[/\\\\]", filename)[-1]
        name = name.split(".")[0]
        words = name.split("-")
        for word in words:
            if exists(f"data/words/{word}.json"):
                continue
            elif word in words_not_found:
                continue
            print(word)
            results = get_all(word)
            if isinstance(results, int) and results != 200:
                print(results)
                if results != 404:
                    save_words_not_found(words_not_found)
                    exit(1)
                words_not_found.append(word)
            time.sleep(1)
    save_words_not_found(words_not_found)
