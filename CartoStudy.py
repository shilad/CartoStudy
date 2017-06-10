# -*- coding: latin-1 -*-
import json
import os
import random

import time
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

MOVIES = """Batman v Superman: Dawn of Justice
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
Dirty Dancing""".split('\n')

VERIFICATION = """The Lord of the Rings: The Fellowship of the Ring
Rocky II""".split('\n')

def log(ev, info):
    path = 'logs/%s.log' % (os.getpid())
    tokens = [
        str(time.time()),
        request.args.get('assignmentId', 'None'),
        request.url,
        ev,
        json.dumps(list(request.args.items(multi=True))),
        json.dumps(info)
    ]
    with open(path, 'a') as f:
        f.write('\t'.join(tokens) + '\n')


# Number of movies selected for maps.
# Total maps is NUM_MAPS * 2 + 2 because of nav / content maps and two verification maps
NUM_MAPS = 5

# Number of movies available as drop-down options.
# Total is NUM_CHOICES + 2 because of two verification options
NUM_CHOICES = 10

def myRedirect(func, **args):
    if request.args.get('assignmentId'):
        args['assignmentId'] = request.args.get('assignmentId')
    if request.args.get('seenMovies'):
        args['seenMovies'] = request.args.getlist('seenMovies')
    return redirect(url_for(func.__name__, **args))


@app.route('/consent/preview')
def consentPreview():
    log('page', 'consent/preview')
    return render_template('consentPreview.html')


@app.route('/')
def index():
    if request.args.get('assignmentId', ''):
        return myRedirect(consentShow)
    else:
        return myRedirect(consentPreview)


@app.route('/consent/show')
def consentShow():
    log('page', 'consent/show')
    return render_template('consent.html')


@app.route('/consent/save')
def consentSave():
    assert(request.args.get('assignmentId', ''))
    log('page', 'consent/save')
    return myRedirect(bioShow)


@app.route('/bio/show')
def bioShow():
    assert(request.args.get('assignmentId', ''))
    log('page', 'bio/show')
    return render_template('biographicaldata.html', movies=sorted(MOVIES + VERIFICATION))


@app.route('/bio/save')
def bioSave():
    assert(request.args.get('assignmentId', ''))
    log('page', 'bio/save')
    return myRedirect(instructions)


@app.route('/instructions/show')
def instructions():
    assert(request.args.get('assignmentId', ''))
    log('page', 'instructions/show')
    return render_template('instructions.html')


def getOptions():
    # Ensure things are deterministic
    random.seed(request.args.get('assignmentId') + '_movies')

    # Gets the list of movie options for the given user
    # Remove verification movies (these are managed independently)
    options = sorted(request.args.getlist('seenMovies'))
    for m in VERIFICATION:
        options.remove(m)

    # Add movies to the seen list if necessary..
    all = list(MOVIES)
    random.shuffle(all)
    while len(options) < 10:
        if all[0] not in options:
            options.append(all[0])
        del(all[0])

    # Truncate and add verifications
    options = options[:10] + VERIFICATION

    random.shuffle(options)

    return options


def getMaps():

    # Start with shown options
    options = getOptions()

    # Ensure things are deterministic
    random.seed(request.args.get('assignmentId') + '_maps')

    # Remove verification movies (these are managed independently)
    for m in VERIFICATION:
        options.remove(m)

    maps = [
        'verification/Rocky II.png',
        'verification/The Lord of the Rings: The Fellowship of the Ring.png',
    ]
    for m in options[:5]:
        maps.append('content/cartoScreenshots-' + m + '.png')
        maps.append('nav/cartoScreenshots-' + m + '.png')


    random.shuffle(options)

    return options



@app.route('/map/show/<int:questionNum>')
def mapShow(questionNum):
    assert(request.args.get('assignmentId', ''))
    log('page', 'map/show/' + str(questionNum))
    return render_template('instructions.html')


@app.route('/map/save')
def mapSave():
    pass


@app.url_defaults
def hashed_url_for_static_file(endpoint, values):
    if 'static' == endpoint or endpoint.endswith('.static'):
        filename = values.get('filename')
        if filename:
            if '.' in endpoint:  # has higher priority
                blueprint = endpoint.rsplit('.', 1)[0]
            else:
                blueprint = request.blueprint  # can be None too

            if blueprint:
                static_folder = app.blueprints[blueprint].static_folder
            else:
                static_folder = app.static_folder

            param_name = 'h'
            while param_name in values:
                param_name = '_' + param_name
            values[param_name] = static_file_hash(os.path.join(static_folder, filename))


def static_file_hash(filename):
    return int(os.stat(filename).st_mtime)  # or app.config['last_build_timestamp'] or md5(filename) or etc...

if __name__ == '__main__':
    app.run()
