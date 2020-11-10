from typing import List, Set
from math import log
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from search import Google
from word2vec import Word2Vec
import numpy as np

STOPWORDS = set(stopwords.words('english'))
INDEXED_PAGES = 130000000000000


class WSP:

    def __init__(self, synset, word, num):
        self.synset = synset
        self.word: str = word
        self.pos: chr = synset.pos()
        self.num: int = num
        self.onyms: Set[str] = set()
        self.name = f"{word}.{self.synset.pos}.{num}"
        self.construct_wsp()

    def construct_wsp(self):
        # Synonyms are simply the lemmas from the current synset
        synonyms = self.synset

        # Hyponyms
        hyponyms = []
        hyponyms.extend(self.synset.hyponyms())
        hyponyms.extend(self.synset.instance_hyponyms())

        # Hypernyms
        hypernyms = []
        hypernyms.extend(self.synset.hypernyms())
        hypernyms.extend(self.synset.instance_hypernyms())

        # Meronyms
        meronyms = []
        meronyms.extend(self.synset.part_meronyms())
        meronyms.extend(self.synset.member_meronyms())
        meronyms.extend(self.synset.substance_meronyms())

        # Holonyms
        holonyms = []
        holonyms.extend(self.synset.part_holonyms())
        holonyms.extend(self.synset.member_holonyms())
        holonyms.extend(self.synset.substance_holonyms())

        # Glossary
        definition = [word for word in self.synset.definition() if not word in STOPWORDS]

        # All synsets from the different -onyms
        all_synsets = [synonyms]
        all_synsets.extend(hyponyms)
        all_synsets.extend(hypernyms)
        all_synsets.extend(meronyms)
        all_synsets.extend(holonyms)

        # Gather all of the lemmas for each synset we gathered
        lemmas = []
        for synset in all_synsets:
            lemmas.extend(synset.lemmas())
        for lemma in lemmas:
            self.onyms.add(lemma.name())


class WSG:

    def __init__(self, word):
        self.word: str = word
        # TODO: maybe change this to a dictionary for lookup in the form "dog.n.1"
        self.wsp_list: List[WSP] = []
        self.construct_wsp_list()

    def construct_wsp_list(self):
        sets = wn.synsets(self.word)
        for i, sense in enumerate(sets):
            self.wsp_list.append(WSP(sense, self.word, i))


class WSPComparer:

    @classmethod
    def wsp_similarity(cls, start: WSP, end: WSP):
        total_vector = np.zeros(shape=(300,), dtype=np.float32)
        for word in start.onyms:
            if Word2Vec.contains(word):
                total_vector = np.add(Word2Vec.vector(word), total_vector)
        Word2Vec.add_vector(start.name, total_vector)
        return Word2Vec.similarity(start.name, end.word)

    @classmethod
    def average_distance(cls, start: WSP, end: WSP):
        total_distance = 0
        for word in start.onyms:
            if Word2Vec.contains(word):
                total_distance += cls.distance(word, end.word)
        average_distance = total_distance / len(start.onyms)
        return average_distance

    @classmethod
    def distance(cls, start: str, end: str):
        return Word2Vec.similarity(start, end)

    @classmethod
    def average_ngd(cls, start: WSP, end: WSP):
        total_ngd = 0
        for word in start.onyms:
            total_ngd += cls.ngd(word, end.word)
        average_ngd = total_ngd / len(start.onyms)
        return average_ngd

    @classmethod
    def ngd(cls, start: str, end: str):
        start_hits = Google.get_hits(start)
        end_hits = Google.get_hits(end)
        start_end_hits = Google.get_hits(f"{start} {end}")
        log_start_hits = log(start_hits)
        log_end_hits = log(end_hits)
        log_start_end_hits = log(start_end_hits)
        # max{log(f(x)), log(f(y))} - log(f(x, y))
        # -------------------------------------
        # log(N) - min{log(f(x)), log(f(y))}
        ngd_score = (max(log_start_hits, log_end_hits) - log_start_end_hits) / (
                log(INDEXED_PAGES) - min(log_start_hits, log_end_hits))
        return ngd_score


if __name__ == '__main__':
    # dog = WSG("plane")
    # print(f"{[(x.word, x.pos, x.num) for x in dog.wsp_list]}")
    # print(f"{[x.synset.hyponyms() for x in dog.wsp_list]}")
    dog = WSG("sewing")
    cat = WSG("batting")
    print(cat.wsp_list[1].onyms)
    best_score = 0
    matched_wsp = None
    for wsp in dog.wsp_list:
        score = WSPComparer.average_distance(wsp, cat.wsp_list[1])
        # print(f"{wsp.word}\n -> \n{wsp.onyms}\n -> \nscore: {score}\n")
        if score > best_score:
            best_score = score
            matched_wsp = wsp
    print(f"{matched_wsp.word} -> {best_score} -> {matched_wsp.synset.definition()}\n{matched_wsp.onyms}")
    best_score = 0
    matched_wsp = None
    for wsp in dog.wsp_list:
        score = WSPComparer.wsp_similarity(wsp, cat.wsp_list[1])
        # print(f"{wsp.word}\n -> \n{wsp.onyms}\n -> \nscore: {score}\n")
        if score > best_score:
            best_score = score
            matched_wsp = wsp
    print(f"{matched_wsp.word} -> {best_score} -> {matched_wsp.synset.definition()}\n{matched_wsp.onyms}")
    # print(WSPComparer.average_ngd(plane.wsp_list[0], vehicle.wsp_list[0]))
