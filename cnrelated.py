import json
import time

import requests
from nltk.corpus import stopwords


def get_related_terms(word):
    stop = stopwords.words("english")

    obj = requests.get("http://api.conceptnet.io/c/en/" + word)
    # Add the word itself to the list
    if obj.status_code != 200:
        print(f"Sleeping for one minute because status code is: {obj.status_code}")
        time.sleep(60)
        return get_related_terms(word)
    else:
        obj = obj.json()
        obj_list = [word]
        # Iterate through the edges of the word...
        for i, edges in enumerate(obj["edges"]):
            # If it's english proceed...
            if "language" in obj["edges"][i]["start"] and obj["edges"][i]["start"]["language"] == "en":
                # Reformat the term to be snake case (I don't remember why but I know it was for a reason)
                edge = obj["edges"][i]["start"]["label"]
                terms = edge.split()
                term = "_".join(terms)
                # Add the reformatted term if it isn't already in the list
                if term not in obj_list and term not in stop:
                    obj_list.append(term)
            if "language" in obj["edges"][i]["end"] and obj["edges"][i]["end"]["language"] == "en":
                # Reformat the term to be snake case (I don't remember why but I know it was for a reason)
                edge = obj["edges"][i]["end"]["label"]
                terms = edge.split()
                term = "_".join(terms)
                # Add the reformatted term if it isn't already in the list
                if term not in obj_list and term not in stop:
                    obj_list.append(term)
        return obj_list


def count_types_of(word):
    obj = requests.get("http://api.conceptnet.io/query?end=/c/en/" + word + "&rel=/r/IsA&limit=100")
    if obj.status_code != 200:
        print(f"Sleeping for one minute because status code is: {obj.status_code}")
        time.sleep(60)
        return count_types_of(word)
    else:
        obj = obj.json()
        obj_list = []
        # Iterate through the edges of the word...
        for i, edges in enumerate(obj["edges"]):
            # If it's english proceed...
            if obj["edges"][i]["rel"]["label"] in "IsA":
                if "language" in obj["edges"][i]["start"] and obj["edges"][i]["start"]["language"] == "en":
                    if obj["edges"][i]["start"]["label"] not in word:
                        # Add the term if it isn't already in the list
                        term = obj["edges"][i]["start"]["label"]
                        if term not in obj_list:
                            obj_list.append(term)
        return len(obj_list)


def get_related(word):
    stop = stopwords.words("english")

    obj = requests.get(f"http://api.conceptnet.io/c/en/{word}?limit=300")
    # Add the word itself to the list
    if obj.status_code != 200:
        print(f"Sleeping for one minute because status code is: {obj.status_code}")
        time.sleep(60)
        return get_related(word)
    else:
        obj = obj.json()
        obj_list = {}
        # Iterate through the edges of the word...
        for i, edges in enumerate(obj["edges"]):
            # If it's english proceed...
            if "language" in obj["edges"][i]["start"] and obj["edges"][i]["start"]["language"] == "en":
                # Reformat the term to be snake case (I don't remember why but I know it was for a reason)
                edge = obj["edges"][i]["start"]["term"]
                term = edge.split('/')[-1]
                if word != term:
                    relation = obj["edges"][i]["rel"]["label"]
                    # Add the reformatted term if it isn't already in the list
                    if term not in obj_list and term not in stop:
                        obj_list[term] = {"relation": relation, "start": term, "end": word}
            if "language" in obj["edges"][i]["end"] and obj["edges"][i]["end"]["language"] == "en":
                # Reformat the term to be snake case (I don't remember why but I know it was for a reason)
                edge = obj["edges"][i]["end"]["term"]
                term = edge.split('/')[-1]
                if word != term:
                    relation = obj["edges"][i]["rel"]["label"]
                    # Add the reformatted term if it isn't already in the list
                    if term not in obj_list and term not in stop:
                        obj_list[term] = {"relation": relation, "start": word, "end": term}
        return obj_list


def get_relationship(word1, word2):

    obj = requests.get(f"http://api.conceptnet.io/query?node=/c/en/{word1}&other=/c/en/{word2}")
    # Add the word itself to the list
    if obj.status_code != 200:
        print(f"Sleeping for one minute because status code is: {obj.status_code}")
        time.sleep(60)
        return get_relationship(word1, word2)
    else:
        obj = obj.json()
        return obj["edges"][0]["rel"]["label"]


if __name__ == '__main__':
    # data = get_related("dog")
    # with open("data.json", "w") as file:
    #     json.dump(data, file)
    relationship = get_relationship("crunch", "situation")
    print(relationship)
