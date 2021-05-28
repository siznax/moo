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

import datetime
import json
import logging
import os
import random
import time

from collections import OrderedDict
from urllib.parse import quote, unquote

from flask import Flask, render_template, request, abort, jsonify, redirect
from flask_executor import Executor

from Moo.play import config, lib, search, utils


app = Flask(__name__)
app.config.from_object(config)
app.config['EXECUTOR_PROPAGATE_EXCEPTIONS'] = True

executor = Executor(app)

base = lib.base(app.config)

if base:
    index = lib.index(base)
    albums = lib.albums(base, index)
    alpha = lib.alpha(albums)


@app.before_request
def get_base():
    if 'BASE' not in app.config:
        app.config['BASE'] = lib.base(app.config)


@app.errorhandler(404)
def page_not_found():
    return render_template('404.html', emoji=lib.EMOJI), 404


@app.route('/')
def root():
    if not app.config['BASE']:
        return render_template('base-admin.html')

    try:
        _albums = sorted_albums('year', albums, reverse=True)
        return serve_album(str(index[0]), index, _albums)
    except NameError:
        return 'RESTART required'


@app.route('/admin')
def admin():
    sindex = search.load_search(app.config['SINDEX'])

    ages = {
        'new': utils.file_age(str(index[0])),
        'search': utils.file_age(app.config['SINDEX']),
    }

    updated = None
    if os.path.exists(app.config['SINDEX']):
        mtime = os.path.getmtime(app.config['SINDEX'])
        updated = datetime.datetime.fromtimestamp(mtime)

    return render_template(
        'admin.html',
        albums=albums,
        ages=ages,
        base=base,
        config=app.config,
        emoji=lib.EMOJI,
        sindex=sindex,
        tasks=executor.futures._state('build_search'),
        updated=updated)


@app.route('/album/<path:alkey>')
def album_route(alkey):
    try:
        base = app.config['BASE']
        alkey = '/'.join([base, alkey])

        _index, _albums = subset('artist', albums[alkey]['artist'])

        return serve_album(alkey, _index, _albums)

    except (FileNotFoundError, KeyError):
        abort(404, 'No albums with alkey: {}'.format(alkey))


@app.route('/alpha/<letter>')
def alpha_route(letter):
    _index = list()

    for path in albums:
        art = albums[path].get('artist')
        if art and art[0] == letter:
            _index.append((letter, path))

    _index = [x[1] for x in _index]

    try:
        _albums = lib.albums(_index[0], _index)
        return serve_album(
            _index[0], _index, sorted_albums('artist', _albums))
    except IndexError:
        abort(404, 'No albums matching: {}'.format(letter))


@app.route('/artist/<path:artist>')
def artist_route(artist):
    try:
        _index, _albums = subset('artist', artist)

        salbums = sorted_albums('year', _albums, reverse=True)

        return serve_album(str(_index[0]), _index, salbums)

    except (IndexError, KeyError):
        abort(404, 'No albums with artist: {}'.format(artist))


@app.route('/base')
def base_route():
    return render_template(
        'base.html',
        albums=albums,
        base=app.config['BASE'],
        emoji=lib.EMOJI,
        index=index)


@app.route('/base-admin', methods=['POST'])
def base_admin():
    base_input = request.form.get('base')

    if not os.path.exists(base_input):
        abort(400, f'invalid path: {base_input}')

    app.config['BASE'] = base_input

    lib.base_write(base_input)
    lib.base_link(base_input)

    return redirect('/')


@app.route('/build-search')
def build_route():
    return jsonify(build_search(index, app.config['SINDEX']))


@app.route('/format/<path:encoding>')
def format_route(encoding):
    try:
        _index, _albums = subset('encoding', encoding)
        salbums = sorted_albums('year', _albums, reverse=True)
        return serve_album(str(_index[0]), _index, salbums)
    except IndexError:
        abort(404, 'No albums with encoding: {}'.format(encoding))


@app.route('/genre/<path:label>')
def genre_label(label):
    try:
        _index, _albums = subset('genre', label)
        salbums = sorted_albums('year', _albums, reverse=True)
        return serve_album(str(_index[0]), _index, salbums)
    except IndexError:
        abort(404, 'No albums with genre: {}'.format(label))


@app.route('/history')
def history():
    _ind = list()
    base = app.config['BASE']

    for entry in lib.get_history(base, app.config['HISTORY']):
        _ind.append(os.path.join(base, entry[1:]))

    _ind.reverse()

    _alb = lib.albums(base, _ind)

    return serve_album(_ind[0], _ind, _alb)


@app.route('/img/<path:alkey>')
def img_alkey(alkey):
    try:
        return lib.cover(os.path.join(app.config['BASE'], alkey))
    except TypeError:
        return app.send_static_file('ico/cover.png')


@app.route('/img/track/<tnum>/<path:alkey>')
def img_track(tnum, alkey):
    try:
        _, metadata = album_data(alkey, index)
        mkey = sorted(metadata.keys())[int(tnum) - 1]
        tpath = metadata[mkey]['fpath']
        return lib.cover(os.path.join(base, alkey), tpath)
    except TypeError:
        return app.send_static_file('cover.png')


@app.route('/None')
def none():
    _albums = dict()
    _index = list()

    try:
        for path in albums:
            art = albums[path].get('artist')
            enc = albums[path].get('encoding')
            gen = albums[path].get('genre')
            yar = albums[path].get('year')

            if (art == 'None' or enc == 'None' or gen == 'None'
                    or yar == 'None'):
                _albums[path] = albums[path]
                _index.append(path)

        salbums = sorted_albums('mtime', _albums, reverse=True)

        return serve_album(str(_index[0]), _index, salbums)

    except IndexError:
        abort(404, 'No albums without metadata!')


@app.route('/new')
def new():
    _ind = index[:100]
    _alb = lib.albums(base, _ind)
    return serve_album(str(_ind[0]), _ind, _alb)


@app.route('/random')
def rando():
    ind = random.choice(range(len(index)))
    alkey = str(index[ind])

    try:
        return redirect('/album' + quote(alkey.replace(base, '')))
    except (TypeError, ValueError):
        redirect('/random')  # try again


@app.route('/search', defaults={'terms': None}, methods=['GET', 'POST'])
@app.route('/search/<path:terms>', methods=['GET', 'POST'])
def search_route(terms):

    if request.method == 'POST':
        terms = request.form.get('search-input')

    sindex = search.load_search(app.config['SINDEX'])

    albums, artists, tracks = search.find(base, sindex, terms)

    return render_template(
        'search-results.html',
        albums=albums,
        artists=artists,
        tracks=tracks,
        emoji=lib.EMOJI,
        sindex=sindex,
        terms=terms)


@app.route('/track/<tnum>/<path:alkey>')
def track(tnum, alkey):
    alkey = '/'.join([base, unquote(alkey)])

    try:
        g_index, g_albums = subset('genre', albums[alkey]['genre'])
        return serve_album(alkey, g_index, g_albums, tnum)
    except:
        abort(404)


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


@executor.job
def build(albindex):
    '''
    build search index from album index and write to outfile
    '''
    logging.info(f"Started build job {time.strftime('%X')}")

    outfile = app.config['SINDEX']
    start = time.time()
    sindex = search.search_index(albindex)
    seconds = int(time.time() - start)

    out = {
        'length': len(sindex),
        'output': outfile,
        'seconds': seconds}

    logging.info('>> Moodex {}'.format(out))

    data = out
    data['results'] = sindex

    with open(outfile, 'w') as _:
        _.write(json.dumps(data))
        logging.info(f"Wrote {_.tell()} bytes to {outfile}")

    logging.info(f"Finished build job {time.strftime('%X')}")

    return out


################################################################


def album_data(alkey, index):
    '''
    returns album, metadata tuple or aborts
    '''
    alb = lib.album(alkey, index)

    if not alb:
        abort(404)

    try:
        return alb, lib.metadata(app.config['BASE'], alb)
    except FileNotFoundError:
        abort(404)


def build_search(index):
    '''
    submit a build_search task (if not running) or return the result
    '''
    result = build_search_result()

    if result:
        return result

    build.submit_stored('build_search', index)

    return f"Submitted build_search task {time.strftime('%X')}"


def build_search_result():
    '''
    returns build_search task state if running else result
    '''
    if not executor.futures.done('build_search'):
        return executor.futures._state('build_search')

    fut = executor.futures.pop('build_search')

    return fut.result()


def serve_album(alkey, index, albums, track_num=1):
    '''
    serve album and selected (or first) track and (all) or part of the
    <index> and <albums>
    '''
    album, data = album_data(alkey, index)

    if data:
        tind = int(track_num) - 1
        dkey = sorted(data.keys())[tind]
        control = lib.control(app.config['BASE'], index, data, tind)
        track = data.get(dkey)
        info = lib.album_info(track, data)
    else:
        if request.path.startswith('/album'):
            abort(404)
        control = None
        track = None
        info = None

    counts = {
        'artist': lib.counts(albums, metakey='artist'),
        'format': lib.counts(albums, metakey='encoding'),
        'genre': lib.counts(albums),
        'year': lib.counts(albums, metakey='year'),
    }

    if request.path.startswith('/track'):
        write_history(alkey)

    return render_template(
        'index.html',
        albums=albums,
        album=album,
        alpha=alpha,
        alkey=alkey.replace(app.config['BASE'], ''),
        base=app.config['BASE'],
        config=app.config,
        control=control,
        counts=counts,
        emoji=lib.EMOJI,
        history=lib.get_history(app.config['BASE'], app.config['HISTORY']),
        index=index,
        info=info,
        metadata=data,
        prefixed=None,  # lib.prefixed(titles),
        total=len(index),
        track=track)


def sorted_albums(sort_key, albums, reverse=False):
    '''
    return albums sorted by sort_key (as OrderedDict)
    '''
    tmp = list()
    nones = list()
    out = OrderedDict()

    for item in albums:
        facet = albums[item].get(sort_key)
        data = albums[item]

        if facet == 'None':
            nones.append((facet, item, data))
        else:
            tmp.append((facet, item, data))

    for tup in sorted(tmp, reverse=reverse):
        out[tup[1]] = tup[2]

    for tup in nones:
        out[tup[1]] = tup[2]

    return out


def subset(facet, value):
    '''
    returns index and albums reduced by metadata <facet> containing <value>
    '''
    base = app.config['BASE']

    sub = list()
    for alb in albums:

        if value == 'None' and not albums[alb][facet]:
            sub.append(alb)
            continue

        if value.lower() in albums[alb][facet].lower():
            sub.append(alb)

    return sub, lib.albums(base, sub)


def write_history(alkey, maxlen=1000):
    '''
    write album or track digest to a HISTORY file when accessed
    '''
    alkey = alkey.replace(app.config['BASE'], '')
    tmp = list()

    with open('HISTORY') as _:
        for line in _:
            if alkey not in line:
                tmp.append(line.strip())

    if not tmp:
        tmp.append(alkey)
    else:
        if tmp[-1] != alkey:
            tmp.append(alkey)

    tmp = tmp[-maxlen:]

    with open('HISTORY', 'w') as _:
        for key in tmp:
            _.write(key + "\n")
