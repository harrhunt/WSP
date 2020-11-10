from optparse import OptionParser
import inspect
from nltk.corpus import wordnet as wn
from wsp import WSG
import numpy as np

if __name__ == '__main__':
    cat = WSG("cat")
    for wsp in cat.wsp_list:
        print(f"{wsp.word}\n{wsp.onyms}\n\n\n")
    # for thing in inspect.getmembers(words[0].lemmas()[0], predicate=inspect.ismethod):
    #     print(thing[0])

    # for word in words:
    #     print(f"{[x.name() for x in word.lemmas()]}")
    #     print(f"{word}")
