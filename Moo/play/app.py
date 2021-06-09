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

from Moo.play import config, lib, utils, MooAlbums, MooSearch


app = Flask(__name__)

app.config.from_object(config)
app.config['EXECUTOR_PROPAGATE_EXCEPTIONS'] = True
app.config['BASE'] = lib.get_base(app.config)

moo = MooAlbums(app.config)
search = MooSearch(app.config)
executor = Executor(app)

logging.basicConfig(level=logging.INFO)


@app.before_request
def before_request():
    '''ensure BASE before every request'''
    if request.method == 'GET' and not app.config.get('BASE'):
        return render_template('base-admin.html')

    return None


@app.errorhandler(404)
def handle_404(err):
    '''render custom 404'''
    return render_template('404.html', emoji=lib.EMOJI), 404


@app.route('/')
def root():
    '''
    render application root
    '''
    salbums = moo.sorted_albums('year', reverse=True)

    return serve_album(str(moo.index[0]), moo.index, salbums)


@app.route('/admin')
def admin():
    '''render admin interface'''
    ages = {
        'new': utils.file_age(str(moo.index[0])),
        'search': utils.file_age(app.config['SINDEX']),
    }

    updated = None

    if os.path.exists(app.config['SINDEX']):
        mtime = os.path.getmtime(app.config['SINDEX'])
        updated = datetime.datetime.fromtimestamp(mtime)

    return render_template(
        'admin.html',
        albums=moo.albums,
        ages=ages,
        base=moo.base,
        config=app.config,
        emoji=lib.EMOJI,
        sindex=search.index,
        tasks=executor.futures._state('build_search'),
        updated=updated)


@app.route('/album/<path:alkey>')
def album_route(alkey):
    '''render album'''
    alkey = '/'.join([app.config['BASE'], alkey])

    try:
        alb = moo.subset('artist', moo.albums[alkey]['artist'])
        ind = list(alb.keys())

        return serve_album(alkey, ind, alb)

    except (FileNotFoundError, KeyError):
        abort(404, 'No albums with alkey: {}'.format(alkey))


@app.route('/alpha/<letter>')
def alpha_route(letter):
    '''render albums with artist starting with letter'''

    # get subset of albums with artists starting with letter
    tmp = dict()
    for path in moo.albums:
        artist = moo.albums[path].get('artist')
        if artist and artist.startswith(letter):
            tmp[path] = moo.albums[path]

    # now sort subset on some key (artist)
    alb = moo.sort_subset(tmp, 'artist')
    ind = list(alb.keys())

    try:
        return serve_album(ind[0], ind, alb)

    except IndexError:
        abort(404, 'No albums matching: {}'.format(letter))


@app.route('/artist/<path:artist>')
def artist_route(artist):
    '''render albums by specified artist'''
    try:
        alb = moo.subset('artist', artist, 'year', True)
        ind = list(alb.keys())

        return serve_album(ind[0], ind, alb)

    except (IndexError, KeyError):
        abort(404, 'No albums with artist: {}'.format(artist))


@app.route('/base')
def base_route():
    '''render the list of albums found'''
    return render_template(
        'base.html',
        albums=moo.albums,
        base=app.config['BASE'],
        emoji=lib.EMOJI,
        index=moo.index)


@app.route('/base-admin', methods=['POST'])
def base_admin():
    '''render the BASE admin interface'''
    base_input = request.form.get('base')

    if not os.path.exists(base_input):
        abort(400, f'invalid path: {base_input}')

    app.config['BASE'] = base_input

    lib.base_write(base_input)
    lib.base_link(base_input)

    moo.base = base_input
    moo.index = moo.albums_index()
    moo.albums = moo.albums_data()
    moo.alpha = moo.albums_alpha()

    search.base = base_input

    return redirect('/')


@app.route('/build-search')
def build_route():
    '''render JSON output from launching search build'''
    return jsonify(build_search(moo.index))


@app.route('/format/<path:encoding>')
def format_route(encoding):
    '''render albums with specified encoding'''
    try:
        alb = moo.subset('encoding', encoding, 'year', True)
        ind = list(alb.keys())

        return serve_album(ind[0], ind, alb)

    except IndexError:
        abort(404, 'No albums with encoding: {}'.format(encoding))


@app.route('/genre/<path:label>')
def genre_label(label):
    '''render albums with specified genre'''
    try:
        alb = moo.subset('genre', label, 'year', True)
        ind = list(alb.keys())

        return serve_album(ind[0], ind, alb)

    except IndexError:
        abort(404, 'No albums with genre: {}'.format(label))


@app.route('/history')
def history():
    '''render albums in HISTORY'''
    base = app.config['BASE']
    ind = list()
    alb = OrderedDict()

    for entry in lib.get_history(base, app.config['HISTORY']):
        ind.append(os.path.join(base, entry[1:]))

    ind.reverse()

    for path in ind:
        if moo.albums.get(path):
            alb[path] = moo.albums[path]

    return serve_album(ind[0], ind, alb)


@app.route('/img/<path:alkey>')
def img_alkey(alkey):
    '''
    send HTTP response with album image data
    '''
    path = os.path.join(app.config['BASE'], alkey)

    try:
        path = os.path.join(app.config['BASE'], alkey)
        return lib.cover(unquote(path))
    except TypeError:
        return app.send_static_file('ico/cover.png')


# @app.route('/img/<tnum>/<path:alkey>')
# def img_track(tnum, alkey):
#     '''send HTTP response with track image data'''
#     try:
#         _, metadata = album_data(alkey)
#         mkey = sorted(metadata.keys())[int(tnum) - 1]
#         tpath = metadata[mkey]['fpath']
#         return lib.cover(os.path.join(app.config['BASE'], alkey), tpath)
#     except TypeError:
#         return app.send_static_file('cover.png')


@app.route('/None')
def none():
    '''render albums with None in a major metadata field'''
    tmp = dict()

    try:
        for path in moo.albums:
            art = moo.albums[path].get('artist')
            enc = moo.albums[path].get('encoding')
            gen = moo.albums[path].get('genre')
            yar = moo.albums[path].get('year')

            if 'None' in [art, enc, gen, yar]:
                tmp[path] = moo.albums[path]

        alb = moo.sort_subset(tmp, 'artist')
        ind = list(alb.keys())
        alk = ind[0]

        return serve_album(alk, ind, alb)

    except IndexError:
        abort(404, 'No albums without metadata!')


@app.route('/new')
def new():
    '''render newly added albums'''
    ind = moo.index[:100]
    alb = dict()

    for path in ind:
        alb[path] = moo.albums.get(path)

    return serve_album(str(ind[0]), ind, alb)


@app.route('/play')
def play():
    '''
    load all other /routes in an iframe for simultaneous play and browse
    '''
    return render_template("play.html")


@app.route('/random')
def rando():
    '''render random album'''
    alkey = str(moo.index[random.choice(range(len(moo.index)))])

    try:
        return redirect('/album' + quote(alkey.replace(moo.base, '')))
    except (TypeError, ValueError):
        redirect('/random')  # try again


@app.route('/search', defaults={'terms': None}, methods=['GET', 'POST'])
@app.route('/search/<path:terms>', methods=['GET', 'POST'])
def search_route(terms):
    '''render search results'''
    if request.method == 'POST':
        terms = request.form.get('search-input')

    albums, artists, tracks = search.find(terms)

    return render_template(
        'search-results.html',
        albums=albums,
        artists=artists,
        tracks=tracks,
        emoji=lib.EMOJI,
        sindex=search.index,
        terms=terms)


@app.route('/track/<tnum>/<path:alkey>')
def track_route(tnum, alkey):
    '''render track'''
    alkey = '/'.join([moo.base, unquote(alkey)])

    try:
        alb = moo.subset('genre', moo.albums[alkey]['genre'])
        return serve_album(alkey, list(alb.keys()), alb, tnum)

    except FileNotFoundError:
        abort(404)


@app.route('/year/<path:year>')
def year_route(year):
    '''render albums for specified year'''
    try:
        sub = moo.subset('year', year)

        if year == 'None':
            alb = moo.sort_subset(sub, 'mtime', True)
        else:
            alb = moo.sort_subset(sub, 'artist')

        ind = list(alb.keys())

        return serve_album(ind[0], ind, alb)

    except IndexError:
        abort(404, 'No albums with year: {}'.format(year))


@executor.job
def build(albindex):
    '''
    build search index from album index and write to outfile
    '''
    logging.info("Started build job %s", time.strftime('%X'))

    outfile = app.config['SINDEX']

    start = time.time()
    sindex = search.search_index(albindex)
    seconds = int(time.time() - start)

    out = {
        'length': len(sindex),
        'output': outfile,
        'seconds': seconds}

    logging.info('>> Moodex %s', out)

    data = out
    data['results'] = sindex

    search.index = data

    with open(outfile, 'w') as _:
        _.write(json.dumps(data))
        logging.info('Wrote %d bytes to %s', _.tell(), outfile)

    logging.info('Finished build job %s', time.strftime('%X'))

    return out


################################################################


def build_search(index):
    '''
    submit a build_search task (if not running) or return the result
    '''
    result = build_search_result()

    if result:
        return result

    build.submit_stored('build_search', index)

    return 'Submitted build_search task %s' % time.strftime('%X')


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
    album, data = album_data(alkey)

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
        alpha=moo.alpha,
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


def album_data(path):
    '''
    return (alkey, metadata) tuple from album path
    '''
    if path not in moo.index:
        abort(404)

    try:
        return path, moo.metadata(path)
    except FileNotFoundError:
        abort(404)
