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

from collections import OrderedDict
from urllib.parse import quote, unquote

from flask import Flask, Response, render_template, request, abort
from flask import redirect, url_for
from Moo.play import config, lib


app = Flask(__name__)
app.config.from_object(config)

base = app.config['BASE']
index = lib.index(app.config)
total = len(index)
albums = lib.albums(base, index)

alpha = lib.alpha(albums)
genres = lib.counts(albums)
artists = lib.counts(albums, metakey='artist')
encodings = lib.counts(albums, metakey='encoding')
years = lib.counts(albums, metakey='year')


@app.route('/')
def root():
    return serve_album(str(index[0]), index, albums)


@app.route('/alpha/<letter>')
def alpha_route(letter):
    _index = list()

    for path in albums:
        art = albums[path].get('artist')
        if art and art[0] == letter:
            _index.append((letter, path))

    _index = sorted(_index)
    _index = [x[1] for x in _index]

    try:
        _albums = lib.albums(_index[0], _index)
        return serve_album(
            _index[0], _index, sorted_albums('artist', _albums))
    except IndexError:
        abort(404, 'No albums matching: {}'.format(letter))


@app.route('/album/<path:alkey>')
def album_route(alkey):
    alkey = '/'.join([base, alkey])

    try:
        _index, _albums = subset('artist', albums[alkey]['artist'])
        return serve_album(alkey, _index, _albums)
    except KeyError:
        abort(404, 'No albums with alkey: {}'.format(alkey))


@app.route('/base')
def base_route():
    return render_template(
        'base.html', albums=albums, base=base, emoji=lib.EMOJI, index=index)


@app.route('/docs', defaults={'doc': None})
@app.route('/docs/<doc>')
def docs_route(doc):
    return render_template('docs.html', emoji=lib.EMOJI)


@app.route('/artist/<path:artist>')
def artist_route(artist):
    try:
        _index, _albums = subset('artist', artist)

        if artist == 'None':
            salbums = sorted_albums('mtime', _albums, reverse=True)
        else:
            salbums = sorted_albums('artist', _albums)

        return serve_album(str(_index[0]), _index, salbums)

    except (IndexError, KeyError):
        abort(404, 'No albums with artist: {}'.format(artist))


@app.route('/format/<path:encoding>')
def format_route(encoding):
    try:
        _index, _albums = subset('encoding', encoding)

        if encoding == 'None':
            salbums = sorted_albums('mtime', _albums, reverse=True)
        else:
            salbums = sorted_albums('artist', _albums)

        return serve_album(str(_index[0]), _index, salbums)

    except IndexError:
        abort(404, 'No albums with encoding: {}'.format(encoding))


@app.route('/genre/<path:label>')
def genre_label(label):
    try:
        _index, _albums = subset('genre', label)

        if label == 'None':
            salbums = sorted_albums('mtime', _albums, reverse=True)
        else:
            salbums = sorted_albums('artist', _albums)

        return serve_album(str(_index[0]), _index, salbums)

    except IndexError:
        abort(404, 'No albums with genre: {}'.format(label))


@app.route('/year/<path:year>')
def year_route(year):
    try:
        _index, _albums = subset('year', year)

        if year == 'None':
            salbums = sorted_albums('mtime', _albums, reverse=True)
        else:
            salbums = sorted_albums('artist', _albums)

        return serve_album(str(_index[0]), _index, salbums)

    except IndexError:
        abort(404, 'No albums with year: {}'.format(year))


@app.route('/img/<path:alkey>')
def img_alkey(alkey):
    try:
        return lib.cover(os.path.join(base, alkey))
    except TypeError:
        return app.send_static_file('ico/cover.png')


@app.route('/img/track/<tnum>/<path:alkey>')
def img_track(tnum, alkey):
    try:
        album, metadata = album_data(alkey, index)
        mkey = sorted(metadata.keys())[int(tnum) - 1]
        tpath = metadata[mkey]['fpath']
        return lib.cover(os.path.join(base, alkey), tpath)
    except TypeError:
        return app.send_static_file('cover.png')


@app.route('/None')
def no_metadata():
    _albums = dict()
    _index = list()

    try:
        for path in albums:
            art = albums[path].get('artist')
            enc = albums[path].get('encoding')
            gen = albums[path].get('genre')
            yar = albums[path].get('year')

            if (art == 'None' 
                or enc == 'None'
                or gen == 'None'
                or yar == 'None'):
                _albums[path] = albums[path]
                _index.append(path)

        salbums = sorted_albums('mtime', _albums, reverse=True)

        return serve_album(str(_index[0]), _index, salbums)

    except IndexError:
        abort(404, 'No albums without metadata!')


@app.route('/random')
def rando():
    ind = random.choice(range(len(index)))
    alkey = str(index[ind])

    try:
        album, metadata = album_data(alkey, index)
        return redirect('/album' + quote(alkey.replace(base, '')))
    except (TypeError, ValueError):
        redirect('/random')  # try again


@app.route('/track/<tnum>/<path:alkey>')
def track(tnum, alkey):
    alkey = '/'.join([base, unquote(alkey)])

    try:
        g_index, g_albums = subset('genre', albums[alkey]['genre'])
        return serve_album(alkey, g_index, g_albums, tnum)
    except:
        abort(404)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', emoji=lib.EMOJI), 404


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


def serve_album(alkey, index, albums, track_num=1):
    '''
    serve album and selected (or first) track and (all) or part of the
    <index> and <albums>
    '''
    album, data = album_data(alkey, index)

    tind = int(track_num) - 1
    dkey = sorted(data.keys())[tind]
    control = lib.control(base, index, data, tind)

    track = data[dkey]
    info = lib.info(track, data)

    counts = {
        'artist': lib.counts(albums, metakey='artist'),
        'format': lib.counts(albums, metakey='encoding'),
        'genre': lib.counts(albums),
        'year': lib.counts(albums, metakey='year'),
    }

    titles = [data[x]['title'] for x in sorted(data)]

    return render_template(
        'index.html',
        albums=albums,
        album=album,
        alpha=alpha,
        alkey=alkey.replace(base, ''),
        base=base,
        control=control,
        counts=counts,
        emoji=lib.EMOJI,
        genre_buttons=app.config['GENRE_BUTTONS'],
        index=index,
        info=info,
        metadata=data,
        prefixed=None,  # lib.prefixed(titles),
        total=total,
        track=track)


def sorted_albums(sort_key, albums, reverse=False):
    '''
    return albums sorted by sort_key (as OrderedDict)
    '''
    tmp = list()
    out = OrderedDict()

    for item in albums:
        facet = albums[item].get(sort_key)
        key = item
        data = albums[item]
        tmp.append((facet, key, data))

    for tup in sorted(tmp, reverse=reverse):
        out[tup[1]] = tup[2]

    return out


def subset(facet, value):
    '''
    returns index and albums reduced by metadata <facet> containing <value>
    '''
    sub = list()

    for alb in albums:

        if value == 'None' and not albums[alb][facet]:
            sub.append(alb)
            continue

        if value.lower() in albums[alb][facet].lower():
            sub.append(alb)
    
    return sub, lib.albums(base, sub)
