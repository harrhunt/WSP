from optparse import OptionParser
import inspect
from nltk.corpus import wordnet as wn
from wsp import WSG
import numpy as np
import json
from os import listdir
from cnrelated import get_relationship
import glob


def create_csv(path):
    headers = ["word_1", "def_1-1", "qual_1-1_start", "qual_1-1_end", "def_1-2", "qual_1-2_start", "qual_1-2_end",
               "def_1-3", "qual_1-3_start", "qual_1-3_end", "def_1-4", "qual_1-4_start", "qual_1-4_end", "def_1-5",
               "qual_1-5_start", "qual_1-5_end", "def_1-6", "qual_1-6_start", "qual_1-6_end", "def_1-7",
               "qual_1-7_start", "qual_1-7_end", "word_2", "def_2-1", "qual_2-1_start", "qual_2-1_end", "def_2-2",
               "qual_2-2_start", "qual_2-2_end", "def_2-3", "qual_2-3_start", "qual_2-3_end", "def_2-4",
               "qual_2-4_start", "qual_2-4_end", "def_2-5", "qual_2-5_start", "qual_2-5_end", "def_2-6",
               "qual_2-6_start", "qual_2-6_end", "def_2-7", "qual_2-7_start", "qual_2-7_end", "relationship"]
    files = glob.glob(f"{path}*.json")
    lines = [",".join(headers)]
    for file in files:
        name = file.split("/")[-1]
        print(name)
        name = name.split(".")[0]
        words = name.split("-")
        if len(words) != 2:
            break
        word1 = WSG(words[0])
        word2 = WSG(words[1])
        line = [f"{word1.word}"]
        for i in range(7):
            if i < len(word1.wsp_list):
                line.append(f'"{word1.wsp_list[i].definition}"')
                line.append("")
                line.append("")
            else:
                line.append("")
                line.append("<!--")
                line.append("-->")
        line.append(f"{word2.word}")
        for i in range(7):
            if i < len(word2.wsp_list):
                line.append(f'"{word2.wsp_list[i].definition}"')
                line.append("")
                line.append("")
            else:
                line.append("")
                line.append("<!--")
                line.append("-->")
        line.append(f"{get_relationship(word1.word, word2.word)}")
        lines.append(",".join(line))
    output = "\n".join(lines)
    with open("survey.csv", "w") as fd:
        fd.write(output)


if __name__ == '__main__':
    create_csv("data/comparisons/")
    # cat = WSG("cat")
    # for wsp in cat.wsp_list:
    #     print(f"{wsp.word}\n{wsp.onyms}\n\n\n")
    # for thing in inspect.getmembers(words[0].lemmas()[0], predicate=inspect.ismethod):
    #     print(thing[0])

    # for word in words:
    #     print(f"{[x.name() for x in word.lemmas()]}")
    #     print(f"{word}")
