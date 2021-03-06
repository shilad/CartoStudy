# -*- coding: latin-1 -*-
import json
import os
import random


import codecs
import time
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__, static_url_path='/CartoStudy/static')

MOVIES = u"""Batman v Superman: Dawn of Justice
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
Amelie
Crimson Peak
All About Eve
Beetlejuice
Super Size Me
An Inconvenient Truth
Close Encounters of the Third Kind
Dirty Dancing""".split('\n')

VERIFICATION = u"""The Lord of the Rings: The Fellowship of the Ring
Rocky II""".split('\n')

for m in MOVIES:
    f1 = 'static/images/maps/content/cartoScreenshots-' + m + '.jpg'
    f2 = 'static/images/maps/nav/cartoScreenshots-' + m + '.jpg'
    assert os.path.isfile(f1), 'could not find ' + f1
    assert os.path.isfile(f2), 'could not find ' + f2

def log(ev, info):
    path = 'logs/%s.log' % (os.getpid())
    tokens = [
        str(time.time()),
        request.args.get('workerId', 'None'),
        request.url,
        ev,
        json.dumps(info),
        json.dumps(list(request.args.items(multi=True))),
    ]
    with codecs.open(path, 'a', encoding='utf-8') as f:
        f.write('\t'.join(tokens) + '\n')


# Number of movies selected for maps.
# Total maps is NUM_MAPS * 2 + 2 because of nav / content maps and two verification maps
NUM_MAPS = 5

# Number of movies available as drop-down options.
# Total is NUM_CHOICES + 2 because of two verification options
NUM_CHOICES = 10

def myRedirect(func, **args):
    if request.args.get('workerId'):
        args['workerId'] = request.args.get('workerId')
    if request.args.get('seenMovies'):
        args['seenMovies'] = request.args.getlist('seenMovies')
    return redirect(url_for(func.__name__, **args))


def testGetOptions():
    for i in range(100):
        for j in range(20):
            workerId = str(random.randint(1, 10000000))
            all = list(MOVIES)
            random.shuffle(all)
            seen = all[:j]

            opts = getOptions(workerId, seen)
            assert(len(opts) == NUM_CHOICES + 2)
            assert(len(opts) == len(set(opts)))
            for v in VERIFICATION:
                assert(v in opts)

            unseen = set(opts) - set(seen) - set(VERIFICATION)
            if unseen:
                assert(len(unseen) + len(seen) == NUM_CHOICES)

            opts2 = getOptions(workerId, seen)

            assert(opts == opts2)


def getOptions(workerId=None, seenMovies=None):
    if workerId is None:
        workerId = request.args.get('workerId')
    if seenMovies is None:
        seenMovies = request.args.getlist('seenMovies')

    # Ensure things are deterministic
    random.seed(workerId + '_options')

    # Gets the list of movie options for the given user
    # Remove verification movies (these are managed independently)
    options = sorted(seenMovies)
    for m in VERIFICATION:
        if m in options:
            options.remove(m)

    # Add movies to the seen list if necessary..
    all = list(MOVIES)
    random.shuffle(all)
    while len(options) < NUM_CHOICES:
        if all[0] not in options:
            options.append(all[0])
        del(all[0])

    # Truncate and add verifications
    random.shuffle(options)
    options = options[:NUM_CHOICES] + VERIFICATION

    return sorted(options)


def getMaps(workerId=None, seenMovies=None):
    # Start with shown options
    options = getOptions(workerId, seenMovies)

    if workerId is None:
        workerId = request.args.get('workerId')

    # Ensure things are deterministic
    random.seed(workerId + '_maps')
    random.shuffle(options)

    # Remove verification movies (these are managed independently)
    for m in VERIFICATION:
        options.remove(m)

    maps = [ ('verification/' + m + '.jpg') for m in VERIFICATION ]

    for m in options[:NUM_MAPS]:
        maps.append('content/cartoScreenshots-' + m + '.jpg')
        maps.append('nav/cartoScreenshots-' + m + '.jpg')

    assert(len(maps) == NUM_MAPS * 2 + 2)

    random.shuffle(maps)

    return maps

@app.route('/')
@app.route('/CartoStudy')
@app.route('/CartoStudy/')
def index():
    return myRedirect(consentShow)


@app.route('/CartoStudy/consent/show')
def consentShow():
    log('page', 'consent/show')
    return render_template('consent.html', movies=sorted(MOVIES + VERIFICATION), numChoices=NUM_CHOICES)


@app.route('/CartoStudy/consent/save')
def consentSave():
    assert(request.args.get('workerId', ''))
    log('page', 'consent/save')
    return myRedirect(bioShow)


@app.route('/CartoStudy/bio/show')
def bioShow():
    assert(request.args.get('workerId', ''))
    log('page', 'bio/show')
    return render_template('biographicaldata.html', movies=sorted(MOVIES + VERIFICATION))


@app.route('/CartoStudy/bio/save')
def bioSave():
    assert(request.args.get('workerId', ''))
    log('page', 'bio/save')
    return myRedirect(instructions)


@app.route('/CartoStudy/instructions/show')
def instructions():
    assert(request.args.get('workerId', ''))
    log('page', 'instructions/show')
    return render_template('instructions.html')



@app.route('/CartoStudy/map/show/<int:questionNum>')
def mapShow(questionNum):
    assert(request.args.get('workerId', ''))
    maps = getMaps()
    options = getOptions()

    log('page', 'map/show/' + str(questionNum))
    return render_template('map.html',
                           totalMaps=(NUM_MAPS*2 + 2),
                           questionNum=questionNum,
                           options=options,
                           map=maps[questionNum])


@app.route('/CartoStudy/map/save/<int:questionNum>')
def mapSave(questionNum):
    assert(request.args.get('workerId', ''))
    maps = getMaps()
    options = getOptions()
    log('map',{ 'map' : maps[questionNum],
                'num' : questionNum,
                'first' : request.args.get('firstchoice', '')
                })

    if questionNum + 1 >= NUM_MAPS * 2 + 2:
        return myRedirect(thanksShow)
    else:
        return myRedirect(mapShow, questionNum=questionNum+1)


@app.route('/CartoStudy/thanks/show')
def thanksShow():
    assert(request.args.get('workerId', ''))
    random.seed(request.args.get('workerId', '') + '_code')
    code = str(random.randint(10000000000, 99999999999))
    log('page', 'thanks/show')
    log('code', code)
    return render_template('thanks.html', code=code)

@app.route('/CartoStudy/thanks/save')
def thanksSaved():
    code = request.args.get('code')
    log('page', 'thanks/save')
    return render_template('thanks_saved.html', code=code)


# @app.url_defaults
# def hashed_url_for_static_file(endpoint, values):
#     if 'static' == endpoint or endpoint.endswith('.static'):
#         filename = values.get('filename')
#         if filename:
#             if '.' in endpoint:  # has higher priority
#                 blueprint = endpoint.rsplit('.', 1)[0]
#             else:
#                 blueprint = request.blueprint  # can be None too
#
#             if blueprint:
#                 static_folder = app.blueprints[blueprint].static_folder
#             else:
#                 static_folder = app.static_folder
#
#             param_name = 'h'
#             while param_name in values:
#                 param_name = '_' + param_name
#             values[param_name] = static_file_hash(os.path.join(static_folder, filename))
#
#
# def static_file_hash(filename):
#     return int(os.stat(filename).st_mtime)  # or app.config['last_build_timestamp'] or md5(filename) or etc...

if __name__ == '__main__':
    app.run()
