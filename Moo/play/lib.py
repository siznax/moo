'''
Methods supporting Moo.play
'''

import hashlib
import json
import os
import random
import string

from io import BytesIO
from math import ceil

from collections import Counter
from pathlib import Path
from unidecode import unidecode
from urllib.parse import quote

import mutagen

from flask import app, send_file, url_for
from .tags import mp3_fields, mp4_fields
from .utils import h_m

# https://developer.mozilla.org/en-US/docs/Web/Media/Formats/Audio_codecs
#
MEDIATYPES = {
    "AAC": "audio/aac",
    "FLAC": "audio/ogg",
    "MP4": "audio/mp4",
    "MP3": "audio/mp3",
    "MPEG": "audio/mpeg",
    "OGG": "audio/ogg",
    "WAV": "audio/wav",
} 


def album(key, index):
    '''
    returns album from index matching key
    '''
    for path in index:
        if str(path).endswith(key):
            return str(path)


def control(base, index, metadata, track_ind):
    '''
    returns next, prev, and random track numbers as dict
    '''
    ntracks = len(metadata)
    _next = track_ind + 2
    prev = track_ind

    if _next > ntracks:
        _next = 0
    
    if prev < 1:
        prev = 0

    ind = random.choice(range(len(index)))
    alkey = str(index[ind]).replace(base, '')

    return {
        'next': _next, 
        'prev': prev,
        'ralbum': alkey,
        'rtrack': random.choice(range(ntracks)) + 1,
        'track_num': track_ind + 1}


def cover(fpath, tpath=None):
    '''
    returns audio file APIC (album cover) data as HTTP response
    '''
    apic = get_apic(fpath, tpath)

    try:
        data = apic.data
        mtype = apic.mime
    except AttributeError:  # try MP4Cover (list of strings)
        data = apic[0]
        mtype = 'image/jpeg'

    return send_file(
        BytesIO(data),
        attachment_filename='apic',
        mimetype=mtype)


def flat_data(mfile, fpath):
    enc = type(mfile).__name__
    tags = dict(mfile.tags)
    flat = dict()

    for item in tags:
        if isinstance(tags[item], list):
            if isinstance(tags[item][0], list):
                flat[item] = ", ".join(tags[item][0])
            else:
                flat[item] = tags[item][0]

    if enc == 'MP3':
        flat = rekey_mp3_tags(flat or tags)

    if enc == 'MP4':
        flat = rekey_mp4_tags(flat or tags)

    flat = rekey_catchall(flat)

    if 'track' in flat:
        flat['track'] = flat_val(flat, 'track')
    
    if 'disc' in flat:
        flat['disc'] = flat_val(flat, 'disc')

    return flat


def flat_val(data, key):
    '''
    returns flattened value from metadata
    '''
    obj = data[key]

    if isinstance(obj, tuple):
        return int(obj[0])

    if isinstance(obj, str):
        try:
            return int(obj)
        except ValueError:
            if '/' in obj:
                return obj.split('/')[0]
            return obj


def get_apic(fpath, tpath=None):
    '''
    returns track image if tpath, else first attached picture
    (APIC) found in tracks
     '''
    def img(track_path):
        try:
            meta = mutagen.File(track_path)
            for tag in meta.tags:
                if tag.startswith('APIC') or tag.startswith('covr'):
                    return meta[tag]
        except AttributeError:
            pass  # not a media file
        except (mutagen.id3.ID3NoHeaderError, mutagen.MutagenError):
            pass  # no ID3 headers

    if tpath:
        track_img = img(tpath)
        if track_img:
            return track_img

    for track in Path(fpath).iterdir():
        track_img = img(str(track))
        if track_img:
            return track_img


def get_term(meta):
    '''
    returns "one good" term from a metadata value
    '''
    excludes = ('album', 'artist', 'artists', 'blue', 'blues', 'from',
                'great', 'jazz', 'music', 'rock', 'song', 'this',
                'unknown', 'various')

    if len(meta.split()) == 1:
        words = [meta]
    else:
        words = meta.split()

    def ascii(word):
        out = word.split("'")[0]  # keep possessive root
        out, _ = os.path.splitext(out)  # drop extension
        out = "".join([x for x in out if x not in string.punctuation])
        return unidecode(out)

    for _ in words:
        word = ascii(_)
        if len(word) > 3 and word.lower() not in excludes:
            return word


def index(config, sort=None, offset=None, limit=None):
    '''
    returns list of albums (PosixPaths), reverse-sorted by mtime
    albums are paths that do not contain directories
    '''
    offset = offset or 0
    sort_key = os.path.getmtime

    if sort:
        if sort == 'atime':
            sort_key = os.path.getatime
        if sort == 'ctime':
            sort_key = os.path.getctime

    paths = sorted(
        Path(config['BASE']).rglob('*'),
        key=sort_key,
        reverse=True)

    albums = list()  # paths that do not contain directories

    count = 0
    for path in paths:
        leaf = True

        try:
            for child in path.iterdir():
                if child.is_dir():
                    leaf = False
                    continue
        except NotADirectoryError:
            continue

        if leaf:  # and path has children?
            albums.append(path)
            count += 1

        if limit and count >= limit:
            break

    return albums[offset:limit]


def info(track, metadata):
    '''
    returns album info as tuple-list from metadata
    '''
    out = list()
    length = 0.0
    ntracks = len(metadata)
    size = 0

    for meta in metadata:
        length += metadata[meta].get('length', 0.0)
        size += metadata[meta].get('size', 0)

    if 'year' in track:
        out.append(('year', track['year'][:4]))

    if 'genre' in track:
        out.append(('genre', track['genre']))

    out.append(('ntracks', "{} tracks".format(ntracks)))

    if int(length):
        out.append(('length', h_m(int(length))))

    out.append(('size', "{} MB".format(round(size / 1e6, 1))))

    return out


def mediatype(enc):
    '''
    returns mediatype given encoding
    '''
    for mtype in MEDIATYPES:
        if enc.upper().startswith(mtype):
            return MEDIATYPES[mtype]


def metadata(base, album):
    '''
    returns metadata dict for a single track from album path
    '''
    out = dict()

    for ind, fpath in enumerate(sorted(Path(album).iterdir())):
        key = str(fpath)
        audio = mutagen.File(fpath)
        encoding = type(audio).__name__
        data = dict()

        if not hasattr(audio, 'tags'):
            continue

        try:
            data = flat_data(audio, fpath)
            data.update(vars(audio.info))
            data['type'] = audio.mime[0]
        except (AttributeError, TypeError):
                pass

        data['encoding'] = encoding
        data['src'] = quote(key.replace(base, '/static/Moo'))

        if 'title' not in data:
            name, ext = os.path.splitext(fpath.name)
            data['title'] = name

        if 'track' not in data:
            data['track'] = ind + 1

        data.update(stat(str(fpath)))

        out[key] = data

    out = parse_fnames(out)

    return sorted_tracks(out)
    

def parse_fnames(mdata):
    updated = False
    words = Counter()
    dashes = Counter()

    for item in mdata:
        if 'title' in mdata[item]:
            continue

        path = Path(mdata[item]['fpath'])

        pwords = path.name.split()
        pdash = path.name.split('-')

        tmp = dict()
        tmp['title'] = path.name

        words.update(pwords)
        dashes.update(pdash)

        mdata[item].update(tmp)
        updated = True

    if not updated:
        return mdata

    for item in mdata:
        mdata[item]['_words'] = dict(words)
        mdata[item]['_dashes'] = dict(dashes)

    return mdata


def personnel(metadata):
    '''
    return set of personnel in album metadata
    '''
    _ = set()

    for item in metadata:
        track = metadata[item]

        if track.get('artist'):
            _.add(track['artist'])
        if track.get('composer'):
            _.add(track['composer'])
        if track.get('conductor'):
            _.add(track['conductor'])

    return list(_)


def rekey_catchall(tags):
    fields = {
        'discnumber': 'disc',
        'tracknumber': 'track',
    }

    _ = dict()

    for item in tags:
        if item in fields:
            key = fields[item]
        else:
            key = item
        _[key] = tags[item]

    return _

def rekey_mp3_tags(tags):
    '''
    normalize MP3 tags to ID3
    '''
    def get_val(obj):
        if hasattr(obj, 'text'):
            text = obj.text
            if isinstance(text, list):
                return ", ".join([str(x) for x in text])
            else:
                return str(text)
        else:
            return str(obj)

    _ = dict()

    for item in tags:
        if item.startswith('APIC'):
            _['APIC'] = tags[item].mime
            continue
        if 'MusicBrainz' in item:
            _['MBID'] = tags[item]
            continue
        if 'purl' in item:
            _['URL'] = tags[item]
            continue
        for field in mp3_fields:
            if item.startswith(field):
                _[mp3_fields[field]] = get_val(tags[item])

    return _


def rekey_mp4_tags(tags):
    '''
    normalize MP4 tags to ID3
    '''
    _ = dict()

    for item in tags:
        if item in mp4_fields:
            _[mp4_fields[item]] = tags[item]

    return _


def related(index, terms):
    '''
    returns index pruned by search term
    '''
    _ = list()

    for path in index:
        dpath = unidecode(str(path).lower())
        for term in terms:
            if term.lower() in dpath:
                    _.append(path)

    return list(set(_))


def sorted_tracks(meta):
    '''
    returns album metadata as dict 
    with keys sorted by track, disc number
    '''
    discs = list()
    ntracks = len(meta)
    out = dict()
    zeroes = 2 if ntracks < 100 else 3
    numbers = list(range(1, ntracks + 1))

    for track in meta:
        if 'disc' in meta[track]:
            discs.append(meta[track]['disc'])

    discs = list(set(discs))

    for ind, track in sorted(enumerate(meta)):
        if 'track' in meta[track]:
            tnum = meta[track]['track']
            try:
                numbers.remove(int(tnum))
            except ValueError:
                tnum = numbers.pop(0)
        else:
            tnum = numbers.pop(0)

        if isinstance(tnum, int):
            tnum = str(tnum)
        else:
            tnum = tnum.split('/')[0].zfill(zeroes)

        if 'disc' in meta[track] and len(discs) > 1:
            dnum = str(meta[track]['disc']).zfill(zeroes)
            key = '{}.{}'.format(dnum, tnum.zfill(zeroes))
        else:
            key = tnum.zfill(zeroes)

        # print('ind = {}, tnum = {} {}'.format(ind, tnum, numbers))

        out[key] = meta[track]
        out[key]['fname'] = track
        out[key]['_key'] = key

    if len(out) != ntracks:
        raise ValueError("Problem sorting tracks {} != {}".format(
            len(out), ntracks))

    return out


def stat(fpath):
    '''returns file stat data as dict'''
    stat = os.stat(fpath)
    return {
        'fpath': fpath,
        'atime': stat.st_atime,
        'mtime': stat.st_mtime,
        'size': stat.st_size}


def tags(base, alkey, track):
    '''
    returns all ID3 tags for a single track from album path as dict
    '''
    for fname in Path(os.path.join(base, alkey)).iterdir():
        if track.get('fname') == str(fname):
            audio = mutagen.File(str(fname))

            try:
                tags = dict(audio.tags)
            except TypeError:
                return None

            for item in audio.tags:
                if str(item).upper().startswith('APIC'):
                    tags[item] = audio.tags[item].mime
                elif str(item).upper().startswith('COVR'):
                    tags[item] = vars(audio.tags[item][0])

            return tags

def terms(metadata, track):
    '''
    returns list of "related" search terms from track, album metadata
    '''
    tmp = list()

    if track.get('artist'):
        tmp.append(get_term(track['artist']))

    if track.get('album_artist'):
        tmp.append(get_term(track['album_artist']))

    if track.get('album'):
        tmp.append(get_term(track['album']))

    if track.get('title'):
        tmp.append(get_term(track['title']))
    else:
        if track.get('genre'):
            tmp.append(get_term(track['genre']))

    return sorted(list(set([x for x in tmp if x])))


def tracks(fpath):
    '''
    returns a list of tracks from a filepath
    '''
    return [str(x) for x in Path(fpath).iterdir()]


def update_history(path):
    '''
    writes album path to .history file
    '''
    with open("HISTORY", "w") as _:
        _.write(path + "\n")
