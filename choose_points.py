# -*- coding: latin-1 -*-
#
# Script to generate Movie Samples
#
#
# Samples are:
"""
Batman v Superman: Dawn of Justice
Citizen Kane
Star Trek Beyond
The Social Network
Fight Club
The Departed
The Lego Movie
Dr. Strangelove
Suriya
The Graduate
Cloverfield
Pan's Labyrinth
It's a Wonderful Life
A.I. Artificial Intelligence
Ferris Bueller's Day Off
Shakespeare in Love
Ilaiyaraaja
The Texas Chain Saw Massacre
Napoleon Dynamite
Princess Mononoke
Our Gang
The Notebook
American Graffiti
The Conjuring
There Will Be Blood
Animal House
The Bridge on the River Kwai
The Karate Kid
The Princess and the Frog
Bajirao Mastani
Night of the Living Dead
Chariots of Fire
Amélie
Crimson Peak
All About Eve
Beetlejuice
Super Size Me
An Inconvenient Truth
Close Encounters of the Third Kind
Dirty Dancing
"""

from collections import defaultdict
import random

import pandas as pd
import numpy as np

blacklist = set("""
Return of the Jedi
Back to the Future
The Lord of the Rings: The Return of the King
Raiders of the Lost Ark
The Hunger Games: Catching Fire
Batman: Bad Blood
Baahubali: The Beginning
Indiana Jones and the Last Crusade
GoldenEye
Star Wars: Episode I – The Phantom Menace
The Lord of the Rings: The Fellowship of the Ring
The Empire Strikes Back
Mad Max: Fury Road
Star Wars: Episode III – Revenge of the Sith
Star Trek: The Motion Picture
Quantum of Solace
Jurassic World
Home Alone
Die Hard
Pirates of the Caribbean: At World's End
The Matrix Reloaded
""".split('\n'))

pd.set_option('display.width', 200)

all_skipped = defaultdict(list)

for dir in ('data/movies_nav', 'data/movies_content'):
    coords = pd.read_table(dir + '/coordinates.tsv')
    coords.columns.values[0] = 'id'
    pops = pd.read_table(dir + '/popularity.tsv')
    names = pd.read_table(dir + '/names.tsv')
    names['name'].fillna('Unknown', inplace=True)

    df = pd.merge(left=coords, right=pops)
    df = pd.merge(left=df, right=names)

    skipped = df[df.name.str[-1].isin(list('abcdefghijk'))]
    skipped = skipped.sort_values('popularity', ascending=False)[:120]

    for index, row in skipped.iterrows():
        all_skipped[row['id']].append(row)

skipped = sorted(all_skipped.values(), key=lambda rows: rows[0]['popularity'], reverse=True)
print(skipped[0])
assert(all(len(sk) == 2 for sk in skipped))

results = []

def dist(row1, row2):
    x1, y1 = row1['x'], row1['y']
    x2, y2 = row2['x'], row2['y']
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

for map_infos in skipped:
    closest = (10000, None)
    name = map_infos[0]['name']
    if name in blacklist: continue

    for r in results:
        d1 = dist(map_infos[0], r[0])
        d2 = dist(map_infos[1], r[1])
        d = min(d1, d2)
        if d < closest[0]:
            closest = (d, r)

    if closest[0] < 1:
        print(closest[0], name, 'is too close to ', closest[1][0]['name'])
    else:
        results.append(map_infos)

for rinfo in results[:40]:
    print(rinfo[0]['name'])


        # for cs in coords[i]:

#         for cs in coords:
#             x2, y2 = cs[i]

#                 for (name2, x2, y2) in used_coords:
#                     d = ((x - x2) ** 2 + (y - y2) ** 2) ** 0.5
#                     if d < closest[0]:
#                         closest = (d, name2)
#                 if closest[0] < 1:
#                     print(name, 'is too close to ', closest[1])
#                 else:
#                     results.append(row['name'])
#                     used_coords.add((row['name'], row['x'], row['y']))
#                     used_ids.add(row['id'])
#                     found = True
#
#             skipped.drop(skipped.index[0], inplace=True)
#
# print('\n'.join(sorted(results)))
#
