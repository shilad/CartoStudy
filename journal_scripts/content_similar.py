"""
Analyze data from https://github.com/idio/wiki2vec

Output from this script is the following:


"""

MOVIES = [
    'DBPEDIA_ID/Dirty_Dancing',
    "DBPEDIA_ID/Ferris_Bueller's_Day_Off",
    'DBPEDIA_ID/Night_of_the_Living_Dead'

]

from gensim.models.word2vec import Word2Vec

en = Word2Vec.load("/Users/a558989/Downloads/en_1000_no_stem/en.model")

for movie in MOVIES:
    for (i, (title, score)) in enumerate(en.most_similar(movie, topn=100)):
        print '%d. %s (%.3f)' % (i+1, title, score)