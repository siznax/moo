#!/usr/bin/env python3

'''
Moo.play
~~~~~~~~

Flask app for playing music files

$ workon moo
$ export FLASK_APP=Moo/play/app.py
$ export FLASK_DEBUG=1
$ export FLASK_ENV=development
$ flask run
'''

import os
import random

from urllib.parse import quote

from flask import Flask, Response, render_template, request, abort
from flask import redirect, url_for
from Moo.play import config, lib


app = Flask(__name__)
app.config.from_object(config)
base = app.config['BASE']
index = lib.index(app.config)


@app.route('/')
def root():
    return render_template('index.html', base=base, index=index)


@app.route('/album/<path:alkey>')
def album_route(alkey):
    alb, metadata = album_data(alkey, index)
    return serve_album(alkey, alb, metadata)


@app.route('/index/<letter>')
def alpha_index(letter):
    alpha = list()

    for path in index:
        alname = str(path).replace(base, '')
        if alname.upper().startswith('/' + letter):
            alpha.append(path)

    return render_template('index.html',
                           alpha=letter, base=base,
                           index=sorted(alpha))


@app.route('/covers/<letter>')
def alpha_covers(letter):
    alpha = list()

    for path in index:
        alname = str(path).replace(base, '')
        if alname.upper().startswith('/' + letter):
            alpha.append(path)

    return render_template('covers.html', alpha=letter, base=base,
                           index=sorted(alpha))


@app.route('/covers')
def covers():
    return render_template('covers.html', index=index, base=base)


@app.route('/debug')
def debug():
    return render_template('debug.html', data=index)


@app.route('/img/track/<tnum>/<path:alkey>')
def cover_track(tnum, alkey):
    try:
        album, metadata = album_data(alkey, index)
        mkey = sorted(metadata.keys())[int(tnum) - 1]
        tpath = metadata[mkey]['fpath']
        return lib.cover(os.path.join(base, alkey), tpath)
    except TypeError:
        return app.send_static_file('cover.png')


@app.route('/img/<path:alkey>')
def cover(alkey):
    try:
        return lib.cover(os.path.join(base, alkey))
    except TypeError:
        return app.send_static_file('cover.png')


@app.route('/meta/<path:alkey>')
def meta_route(alkey):
    album, metadata = album_data(alkey, index)
    return metadata


@app.route('/random')
def rando():
    ind = random.choice(range(len(index)))
    alkey = str(index[ind])
    album, metadata = album_data(alkey, index)
    return redirect('/album' + quote(alkey.replace(base, '')))


@app.route('/track/<tnum>/<path:alkey>')
def track(tnum, alkey):
    alb, metadata = album_data(alkey, index)
    return serve_album(alkey, alb, metadata, int(tnum) - 1)


def album_data(alkey, index):
    '''
    returns album, metadata tuple or aborts
    '''
    alb = lib.album(alkey, index)

    if not alb:
        abort(404)

    try:
        metadata = lib.metadata(base, alb)
    except FileNotFoundError:
        abort(404)

    if not metadata:
        raise ValueError('{} has no METADATA'.format(quote(alkey)))

    return alb, metadata


def serve_album(alkey, album, metadata, track_ind=None):

    if track_ind is not None:
        autoplay = True
        lib.update_history(alkey)
    else:
        autoplay = False
        track_ind = 0

    mkey = sorted(metadata.keys())[track_ind]
    tnum = track_ind + 1
    track = metadata[mkey]

    try:
        tags = lib.tags(base, alkey, track)
    except AttributeError:
        raise ValueError("NO TAGS: album/{}".format(quote(alkey)))

    terms = lib.terms(metadata, track)
    control = lib.control(base, index, metadata, track_ind)

    return render_template(
        'album.html',
        album=album,
        alkey=alkey,
        autoplay=autoplay,
        base=base,
        control=control,
        index=index,
        info=lib.info(track, metadata),
        metadata=metadata,
        mkey=mkey,
        personnel=lib.personnel(metadata),
        related=lib.related(index, terms),
        tags=tags,
        terms=terms,
        tnum=tnum,
        track=track)
