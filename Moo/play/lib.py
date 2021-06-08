'''
Methods supporting Moo.play
'''

import logging
import os
import random

from collections import Counter
from io import BytesIO
from pathlib import Path

import mutagen

from flask import send_file

from .utils import hours_minutes


EMOJI = {  # CLDR emoji names
    'admin': "\u2699\uFE0F",  # "\N{Gear}",
    'app': "\N{saxophone}",
    'base': '&#x1F3B5;',
    'fleuron': '&#x2766;',
    'heart': "\N{black heart suit}",
    'hearted': "\N{anatomical heart}",
    'help': '&#x2754;',
    'history': '&#x1F3B6;',
    'more': '&#x1F52E;',
    'next': "\N{Black Right-Pointing Double Triangle with Vertical Bar}",
    'new': '&#x1F195;',
    'none': '&#x1F6AB;',
    'notfound': '&#x1F62D;',
    'prev': "\N{Black Left-Pointing Double Triangle with Vertical Bar}",
    'random': '&#x1F3B2;',
    'run': '&#x1F6FC;',
    'search': '&#x1F50D;',
    'shades': '&#x1F576;',
    'star': '&#x2606;',
    'starred': '&#x2B50;',
}

# https://developer.mozilla.org/en-US/docs/Web/Media/Formats/Audio_codecs
MEDIATYPES = {
    "AAC": "audio/aac",
    "FLAC": "audio/ogg",
    "MP3": "audio/mp3",
    "MP4": "audio/mp4",
    "MPEG": "audio/mpeg",
    "OGG": "audio/ogg",
    "WAV": "audio/wav",
}


def album_info(track, metadata):
    '''
    returns dict of album info
    '''
    first_artist = None
    length = 0.0
    out = dict()
    size = 0

    for meta in metadata:
        length += metadata[meta].get('length', 0.0)
        size += metadata[meta].get('size', 0)

        if not first_artist:
            first_artist = metadata[meta].get('artist')

        if metadata[meta].get('artist') != first_artist:
            out['various'] = True

    artist = track.get('album_artist') or track.get('artist')

    out['album'] = track.get('album')
    out['artist'] = artist.split(';')[0] if artist else None
    out['encoding'] = track.get('encoding')
    out['genre'] = track.get('genre')
    out['ntracks'] = len(metadata)

    if 'year' in track:
        out['year'] = track['year'][:4]

    if int(length):
        out['length'] = hours_minutes(int(length))

    out['size'] = "{}MB".format(round(size / 1e6, 1))

    return out


def base_link(base):
    '''
    makes symbolic link to BASE in Moo/play/static
    '''
    dst = os.path.join(os.getcwd(), 'Moo', 'play', 'static', 'Moo')

    if not os.path.exists(base):
        raise ValueError(f"BASE not found: {base}")

    logging.info('Linking BASE to static/Moo')
    logging.info('> os.symlink(%s, %s)', base, dst)

    if os.path.exists(dst):
        if not os.path.islink(dst):
            raise ValueError(f'Directory exists: {dst}')
        os.unlink(dst)

    os.symlink(base, dst, target_is_directory=True)


def base_write(base):
    '''
    write base input to BASE file
    '''
    with open('BASE', 'w') as _:
        _.write(base)


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


def counts(albums, metakey='genre', limit=None):
    '''
    returns counter of genres from albums
    '''
    count = Counter()

    for item in albums:
        count[albums[item].get(metakey) or 'None'] += 1

    if limit:
        for item in count:
            if count[item] > limit:
                del count[item]

    return dict(count)


def cover(fpath, tpath=None):
    '''
    returns audio file APIC (album cover) data as HTTP response
    '''
    logging.info('lib.cover fpath = %s', fpath)

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


def get_apic(fpath, tpath=None):
    '''
    returns track image if tpath, else first attached picture
    (APIC) found in tracks
     '''
    def img(track_path):
        try:
            meta = mutagen.File(track_path)

            for tag in dict(meta):
                if tag.startswith('APIC') or tag.startswith('covr'):
                    return meta[tag]

        except AttributeError:
            return None  # not a media file

        except (mutagen.id3.ID3NoHeaderError, mutagen.MutagenError):
            return None  # no ID3 headers

        return None

    if tpath:
        track_img = img(tpath)
        if track_img:
            return track_img

    for track in Path(fpath).iterdir():
        track_img = img(str(track))
        if track_img:
            return track_img

    return None


def get_base(config):
    '''
    returns BASE directory from BASEFILE
    '''
    if not os.path.exists(config['BASEFILE']):
        return None

    with open(config['BASEFILE']) as _:
        return _.read().strip()


def get_history(base, filepath):
    '''
    returns list of recently played albums with valid paths
    '''
    out = list()

    with open(filepath) as _:
        for line in _:
            entry = line.strip()
            if os.path.exists(os.path.join(base, entry[1:])):
                out.append(entry)

        return out


def mediatype(enc):
    '''
    returns mediatype given encoding
    '''
    for mtype in MEDIATYPES:
        if enc.upper().startswith(mtype):
            return MEDIATYPES[mtype]

    return None


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


def prefixed(titles):
    '''
    returns (prefix) nested dict from list of titles, which can vastly
    improve readability of classical music tracks

    Note: this is an experimental feature.

    EXAMPLE INPUT = [
        'Beethoven: Piano Trio #7 In B Flat, Op. 97, "Archduke"
            - 1. Allegro Moderato',
        'Beethoven: Piano Trio #7 In B Flat, Op. 97, "Archduke"
            - 2. Scherzo: Allegro',
        'Beethoven: Piano Trio #7 In B Flat, Op. 97, "Archduke"
            - 3. Andante Cantabile',
        'Beethoven: Piano Trio #7 In B Flat, Op. 97, "Archduke"
            - 4. Allegro Moderato, Presto',
        'Beethoven: Piano Trio #5 In D, Op. 70/1, "Ghost"
            - 1. Allegro Vivace E Con Brio',
        'Beethoven: Piano Trio #5 In D, Op. 70/1, "Ghost"
            - 2. Largo Assai Ed Espressivo',
        'Beethoven: Piano Trio #5 In D, Op. 70/1, "Ghost"
            - 3. Presto'
    ]

    DESIRED OUTPUT = {
        'Beethoven: Piano Trio #7 In B Flat, Op. 97, "Archduke"': {
            '1. Allegro Moderato',
            '2. Scherzo: Allegro',
            '3. Andante Cantabile',
            '4. Allegro Moderato, Presto'}
        'Beethoven: Piano Trio #5 In D, Op. 70/1, "Ghost"': {
            '1. Allegro Vivace E Con Brio',
            '2. Largo Assai Ed Espressivo',
            '3. Presto'}
    '''
    out = dict()

    same = list()
    prefix = None
    suffix = None
    last = list()

    for i, title in enumerate(titles):

        print(i, title)

        if last:
            for j, word in enumerate(title.split()):
                if word == last[j]:
                    same.append(word)
                else:
                    suffix = ' '.join(title.split()[j:])
                    break

            print('  same:', same)
            print('  suffix:', suffix)

            if len(same) > 2 and suffix:
                prefix = ' '.join(same)

                print('   prefix:', prefix)
                print('   suffix:', suffix)

                for item in out:
                    if prefix in item:
                        continue

                if prefix not in out:
                    first_suffix = ' '.join(last).replace(prefix, '').strip()
                    out[prefix] = [first_suffix]

                out[prefix].append(suffix)

        same = list()
        suffix = None
        last = title.split()

    return out


def tags(base, alkey, track_fname):
    '''
    returns all ID3 tags for a single track from album path as dict
    '''
    for fname in Path(os.path.join(base, alkey)).iterdir():
        if track_fname == str(fname):
            audio = mutagen.File(str(fname))

            try:
                _tags = dict(audio.tags)
            except TypeError:
                return None

            for item in audio.tags:
                if str(item).upper().startswith('APIC'):
                    _tags[item] = audio.tags[item].mime
                elif str(item).upper().startswith('COVR'):
                    _tags[item] = vars(audio.tags[item][0])

            return _tags

    return None
