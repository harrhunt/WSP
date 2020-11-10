import inspect
import json
import time
from typing import List, Set
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from word2vec import Word2Vec
import numpy as np

STOPWORDS = set(stopwords.words('english'))


class WSP:

    def __init__(self, synset, word, num):
        self.synset = synset
        self.word: str = word
        self.pos: chr = synset.pos()
        self.num: int = num
        self.onyms: Set[str] = set()
        self.name = f"{word}.{self.pos}.{num}"
        self.definition = synset.definition()
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
        definition = [word for word in self.definition if word not in STOPWORDS]

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

        self.onyms.union(set(definition))


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
    def single_link(cls, start: WSP, end: WSP):
        """
        Smallest distance between any two points in start and end
        :param start: The starting word sense profile (WSP)
        :param end: The ending word sense profile (WSP)
        :return: The cosine similarity of the closest two points in start and end
        """
        # Start at largest possible distance
        shortest_distance = -1

        # Iterate through words in both sets
        for start_word in start.onyms:
            if Word2Vec.contains(start_word):
                for end_word in end.onyms:
                    if Word2Vec.contains(end_word):
                        distance = Word2Vec.similarity(start_word, end_word)
                        # If the distance is shorter, update the shortest distance
                        if distance > shortest_distance:
                            shortest_distance = distance
        return float(shortest_distance)

    @classmethod
    def complete_link(cls, start: WSP, end: WSP):
        """
        Largest distance between any two points in start and end
        :param start: The starting word sense profile (WSP)
        :param end: The ending word sense profile (WSP)
        :return: The cosine similarity of the furthest two points in start and end
        """
        # Start at the shortest possible distance
        greatest_distance = 1

        # Iterate through words in both sets
        for start_word in start.onyms:
            if Word2Vec.contains(start_word):
                for end_word in end.onyms:
                    if Word2Vec.contains(end_word):
                        distance = Word2Vec.similarity(start_word, end_word)
                        # If the distance is larger, update the greatest distance
                        if distance < greatest_distance:
                            greatest_distance = distance
        return float(greatest_distance)

    @classmethod
    def average_link(cls, start: WSP, end: WSP):
        """
        Average distance between any two points in start and end
        :param start: The starting word sense profile (WSP)
        :param end: The ending word sense profile (WSP)
        :return: The average cosine similarity of all pairs of words in start and end
        """
        total_distance = 0

        # Keep track of sizes since some words may not be in W2V and may get skipped...
        # May give inaccurate results otherwise
        size_of_start = 0
        size_of_end = 0
        for start_word in start.onyms:
            if Word2Vec.contains(start_word):
                size_of_start += 1
                for end_word in end.onyms:
                    if Word2Vec.contains(end_word):
                        size_of_end += 1
                        total_distance += Word2Vec.similarity(start_word, end_word)
        # Average distance is equal to all of the distances between
        # each pair of words divided by the product of the number of words in each set
        average_distance = total_distance / (size_of_start * size_of_end)
        return float(average_distance)

    @classmethod
    def total_vector(cls, start: WSP, end: WSP):
        """
        The similarity between all vectors (added) for all words in start and all vectors (added) for all words in end
        :param start: The starting word sense profile (WSP)
        :param end: The ending word sense profile (WSP)
        :return: The cosine similarity of the total vectors for start and end
        """
        start_total_vector = np.zeros(shape=(300,), dtype=float)
        end_total_vector = np.zeros(shape=(300,), dtype=float)
        for start_word in start.onyms:
            if Word2Vec.contains(start_word):
                start_total_vector = np.add(Word2Vec.vector(start_word), start_total_vector)
        for end_word in end.onyms:
            if Word2Vec.contains(end_word):
                end_total_vector = np.add(Word2Vec.vector(end_word), end_total_vector)

        # Add the vector for each WSP to the W2V model and treat them as their own vectors
        Word2Vec.add_vector(start.name, start_total_vector)
        Word2Vec.add_vector(end.name, end_total_vector)
        # Then return the similarity of the two WSPs
        return float(Word2Vec.similarity(start.name, end.name))

    @classmethod
    def average_vector(cls, start: WSP, end: WSP):
        """
        The similarity between all vectors (averaged) for all words in start and all vectors (averaged) for all words in end
        :param start: The starting word sense profile (WSP)
        :param end: The ending word sense profile (WSP)
        :return: The cosine similarity of the average vectors for start and end
        """
        start_total_vector = np.zeros(shape=(300,), dtype=float)
        end_total_vector = np.zeros(shape=(300,), dtype=float)
        size_of_start = 0
        size_of_end = 0
        for start_word in start.onyms:
            if Word2Vec.contains(start_word):
                size_of_start += 1
                start_total_vector = np.add(Word2Vec.vector(start_word), start_total_vector)
        for end_word in end.onyms:
            if Word2Vec.contains(end_word):
                size_of_end += 1
                end_total_vector = np.add(Word2Vec.vector(end_word), end_total_vector)

        # Get the average vector for both the start and end WSPs...
        start_average_vector = np.true_divide(start_total_vector, size_of_start)
        end_average_vector = np.true_divide(end_total_vector, size_of_end)
        # then add them to the W2V model...
        Word2Vec.add_vector(start.name, start_average_vector)
        Word2Vec.add_vector(end.name, end_average_vector)
        # and return the similarity between the two WSPs
        return float(Word2Vec.similarity(start.name, end.name))


COMPARING_METHODS = {x[0]: x[1] for x in inspect.getmembers(WSPComparer, predicate=inspect.ismethod) if
                     x[1].__code__.co_argcount == 3 and {'start', 'end'}.issubset(set(x[1].__code__.co_varnames))}


def test_comparisons(start_word: str, end_word: str):
    start = WSG(start_word)
    end = WSG(end_word)
    data = {}
    start_time = 0
    end_time = 0

    for method in COMPARING_METHODS:
        print(method)
        comparison = COMPARING_METHODS[method]
        best_score = -1
        matched_start_wsp = None
        matched_end_wsp = None
        for start_wsp in start.wsp_list:
            for end_wsp in end.wsp_list:
                start_time = time.time()
                score = comparison(start_wsp, end_wsp)
                end_time = time.time()
                if score > best_score:
                    print(start_wsp.name, end_wsp.name)
                    best_score = score
                    matched_start_wsp = start_wsp
                    matched_end_wsp = end_wsp
        data[method] = {"score": best_score, "time": (end_time - start_time),
                        "start_wsp": {"name": matched_start_wsp.name, "definition": matched_start_wsp.definition,
                                      "onyms": list(matched_start_wsp.onyms)},
                        "end_wsp": {"name": matched_end_wsp.name, "definition": matched_end_wsp.definition,
                                    "onyms": list(matched_end_wsp.onyms)}}
    return data


if __name__ == '__main__':
    word_pairs = [("plane", "mathematics"), ("plane", "machine"), ("batting", "baseball"), ("sewing", "batting"),
                  ("machine", "computer"), ("computer", "memory"), ("memory", "brain"), ("brain", "ideas")]
    for word_pair in word_pairs:
        word1 = word_pair[0]
        word2 = word_pair[1]
        results = test_comparisons(word1, word2)
        with open(f"data/comparisons/{word1}-{word2}.json", "w") as file:
            json.dump(results, file, indent=2)
