import json
from nltk.corpus import stopwords
import random
from cnrelated import get_related
from os import listdir, remove

from wsp import *
from oxford import *

STOPWORDS = set(stopwords.words('english'))


def get_random_relations():
    with open("data/cleaned_words_oxford.json", "r") as file:
        words = json.load(file)
    list_of_relations = []
    for word in words:
        relations = get_related(word)
        edges = list(relations.keys())
        if len(edges) > 0:
            edge = ""
            word_definitions = get_all_coarse_defs(word)
            count = 0
            skip = False
            previous_edge = ""
            while True:
                if len(edges) <= 0:
                    skip = True
                    break
                edge = random.choice(edges)
                edge_definitions = get_all_coarse_defs(edge)
                if edge_definitions is None:
                    skip = True
                    break
                # for definition in edge_definitions:
                #     print(definition)
                # for definition in word_definitions:
                #     print(definition)
                # print("\n\n\n\n")
                if 2 <= len(edge_definitions) <= 5 and not set(word_definitions).issubset(set(edge_definitions)) and not set(edge_definitions).issubset(set(word_definitions)) and relations[edge]["relation"] != "Antonym" and relations[edge]["relation"] != "DistinctFrom":
                    break
                edges.remove(edge)
                if edge == previous_edge:
                    count += 1
                previous_edge = edge
                if count > 10:
                    skip = True
                    break
            if skip:
                continue
            if relations[edge]["start"] == word:
                list_of_relations.append((word, edge))
            else:
                list_of_relations.append((edge, word))
    print(len(list_of_relations))
    with open(f"data/{len(list_of_relations)}_relations.json", "w") as file:
        json.dump(list_of_relations, file)


def pick_n_words(n=1000):
    with open("data/words_list.json", "r") as file:
        cleaned = json.load(file)
    new_list = []
    for i in range(n):
        choice = random.choice(cleaned)
        new_list.append(choice)
        cleaned.remove(choice)
    print(len(new_list))
    with open(f"data/{n}_words.json", "w") as file:
        json.dump(new_list, file)


def clean_dictionary():
    # Words must have the following attributes:
    # Not be a stopword
    # Be in wordnet
    # Have at least 3 WSP and at most 7 WSP
    summary_stats = {}
    summary_stats["total"] = 0
    with open("data/words_list.json", "r") as file:
        words = json.load(file)
    total_size = len(words)
    clean_list = []
    for i, word in enumerate(words):
        if word not in STOPWORDS:
            definitions = get_all_coarse_defs(word)
            if definitions is None:
                continue
            num_defs = len(definitions)
            if num_defs > 10:
                print(definitions)
            if num_defs not in summary_stats:
                summary_stats[num_defs] = {}
                summary_stats[num_defs]["count"] = 0
            summary_stats[num_defs]["count"] += 1
            summary_stats["total"] += 1
            if 2 <= len(definitions) <= 5:
                clean_list.append(word)
            if i % 2000 == 0:
                print(f"{(i / total_size) * 100:.2f}%")
    for stat in summary_stats:
        if stat != "total":
            summary_stats[stat]["proportion"] = (summary_stats[stat]["count"] / summary_stats["total"])
    print(len(clean_list))
    with open("data/cleaned_words_oxford_all.json", "w") as file:
        json.dump(clean_list, file)
    with open("data/oxford_summary_stats.json", "w") as file:
        json.dump(summary_stats, file)


def filter_obscenities_from_file(filename):
    with open("data/obscenities.json", "r") as file:
        obscenities = json.load(file)
    with open(filename, "r") as file:
        words = list(json.load(file))
    to_remove = []
    for word in words:
        if word in obscenities:
            print(word)
            to_remove.append(word)
    for word in to_remove:
        words.remove(word)
    with open(filename, "w") as file:
        json.dump(words, file)


def filter_obscenities():
    with open("data/obscenities.json", "r") as file:
        obscenities = json.load(file)
    path = "data/comparisons/"
    files = listdir(path)
    for file in files:
        name = file.split(".")[0]
        words = name.split("-")
        for word in words:
            if word in obscenities:
                print(file)
                remove(f"{path}{file}")
                break

# def get_random_relations():
#     with open("data/1400_words.json", "r") as file:
#         words = json.load(file)
#     list_of_relations = []
#     for word in words:
#         relations = get_related(word)
#         edges = list(relations.keys())
#         if len(edges) > 0:
#             edge = ""
#             word_synset = wn.synsets(word)
#             count = 0
#             skip = False
#             previous_edge = ""
#             while True:
#                 if len(edges) <= 0:
#                     skip = True
#                     break
#                 edge = random.choice(edges)
#                 edge_synset = wn.synsets(edge)
#                 if 3 <= len(edge_synset) <= 7 and edge_synset != word_synset and relations[edge]["relation"] != "Antonym" and relations[edge]["relation"] != "DistinctFrom":
#                     break
#                 edges.remove(edge)
#                 if edge == previous_edge:
#                     count += 1
#                 previous_edge = edge
#                 if count > 10:
#                     skip = True
#                     break
#             if skip:
#                 continue
#             if relations[edge]["start"] == word:
#                 list_of_relations.append((word, edge))
#             else:
#                 list_of_relations.append((edge, word))
#     print(len(list_of_relations))
#     with open("data/1000_relations.json", "w") as file:
#         json.dump(list_of_relations, file)
#
# def pick_n_words(n=1000):
#     with open("data/cleaned_words.json", "r") as file:
#         cleaned = json.load(file)
#     new_list = []
#     for i in range(n):
#         new_list.append(random.choice(cleaned))
#     print(len(new_list))
#     with open(f"data/{n}_words.json", "w") as file:
#         json.dump(new_list, file)
#
# def clean_dictionary():
#     # Words must have the following attributes:
#     # Not be a stopword
#     # Be in wordnet
#     # Have at least 3 WSP and at most 7 WSP
#     with open("data/words_list.json", "r") as file:
#         words = json.load(file)
#     clean_list = []
#     for word in words:
#         if word not in STOPWORDS:
#             synsets = wn.synsets(word)
#             if 3 <= len(synsets) <= 7:
#                 clean_list.append(word)
#     print(len(clean_list))
#     with open("data/cleaned_words.json", "w") as file:
#         json.dump(clean_list, file)


if __name__ == '__main__':
    clean_dictionary()
    # filter_obscenities_from_file("data/cleaned_words_oxford.json")
    # pick_n_words(100000)
    # get_random_relations()
    # filter_obscenities()
    # word1 = wn.synsets("office")
    # word2 = wn.synsets("offices")
    # print(word1, word2)
    # if word1 == word2:
    #     print("true")
    # new_list = []
    # for i in range(1000):
    #     new_list.append(random.choice(words))

    # with open("data/1000_words.json", "w") as file:
    #     json.dump(new_list, file)
