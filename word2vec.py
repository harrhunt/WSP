from gensim import downloader
import numpy as np


class Word2Vec:
    model = downloader.load('word2vec-google-news-300')

    @classmethod
    def add_vector(cls, key, vector):
        cls.model.wv[key] = vector

    @classmethod
    def vector(cls, word):
        if word in cls.model.vocab:
            return cls.model.word_vec(word)

    @classmethod
    def vectors(cls, words):
        if not isinstance(words, list):
            words = str(words).split()
        vectors = []
        for word in words:
            if word in cls.model.vocab:
                vectors.append(cls.model.word_vec(word))
        return vectors

    # @classmethod
    # def vector_similarity(cls, vector1, vector2):
    #     vector = np.ndarray(shape=(1,))
    #     similarity = cls.model.cosine_similarities(vector1, vector2)
    #     print(f"{similarity}")
    #     return similarity

    @classmethod
    def similarity(cls, word1, word2):
        return cls.model.similarity(word1, word2)

    @classmethod
    def get_distances(cls, words):
        distances = []
        word_pairs = []
        good_words = []
        for word in words:
            if word in cls.model.vocab:
                good_words.append(word)
        for word1 in good_words:
            for word2 in good_words:
                pair = {word1, word2}
                if pair not in word_pairs and len(pair) == 2:
                    word_pairs.append(pair)
        for pair in word_pairs:
            distances.append(cls.model.similarity(pair.pop(), pair.pop()))
        return distances

    @classmethod
    def contains(cls, word):
        return word in cls.model.vocab


if __name__ == '__main__':
    vectora = Word2Vec.vector("hello")
    vectorb = Word2Vec.vector("hi")
    zeros = np.zeros(shape=(300,), dtype=np.float32)
    new_vector = np.add(vectora, zeros)
    new_vector = np.add(vectorb, new_vector)
    print(new_vector)
