'''
Methods supporting Moo.play
'''

import logging
import os
import random
import time

from collections import Counter, OrderedDict
from io import BytesIO
from pathlib import Path
from urllib.parse import quote

import mutagen

from flask import send_file

from .tags import mp3_fields, mp4_fields
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


logging.basicConfig(level=logging.INFO)


def album(key, index):
    '''
    returns album from index matching key
    '''
    for path in index:
        if str(path).endswith(key):
            return str(path)


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


def albums(base, index):
    '''
    returns dict of minimal album metadata
    '''
    logging.info("Getting ALBUMS %s" % time.strftime('%X'))

    out = dict()

    for path in index:
        pobj = Path(path)

        meta = metadata(base, pobj, single=True)

        if not meta.get('album'):
            continue  # index, albums diverge

        artist = meta.get('album_artist') or meta.get('artist')
        year = meta['year'][:4] if meta.get('year') else 'None'

        pruned = {
            'album': meta.get('album'),
            'artist': artist.split(';')[0] if artist else 'None',
            'genre': meta.get('genre') or 'None',
            'mtime': meta.get('mtime', 0),
            'year': year}

        out[path] = pruned

    logging.info(f"ALBUMS DONE {time.strftime('%X')}")

    return out


def alpha(albums, mtag='artist'):
    '''
    returns a map of letters and counts from selected mtag
    '''
    letters = Counter()

    for path in albums:
        alb = albums[path]
        art = alb.get(mtag)
        if art:
            letters[art[0].upper()] += 1

    return dict(letters)


def base(config):
    '''
    returns BASE directory from BASEFILE
    '''
    if not os.path.exists(config['BASEFILE']):
        return

    with open(config['BASEFILE']) as _:
        return _.read().strip()


def base_link(base):
    '''
    makes symbolic link to BASE in Moo/play/static
    '''
    dst = os.path.join(os.getcwd(), 'Moo', 'play', 'static', 'Moo')

    if not os.path.exists(base):
        raise ValueError(f"BASE not found: {base}")

    logging.info('Linking BASE to static/Moo')
    logging.info(f"> os.symlink({base}, {dst})")

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


def flat_data(mfile):
    '''
    returns flattened dict from audio file metadata
    '''
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


def index(base, sort=None):
    '''
    returns list of paths that do not contain directories,
    reverse-sorted by mtime (default), atime, or ctime
    '''
    logging.info(f"Computing INDEX {time.strftime('%X')}")

    albums = list()  # paths that do not contain directories
    sort_key = os.path.getmtime

    if sort:
        if sort == 'atime':
            sort_key = os.path.getatime
        if sort == 'ctime':
            sort_key = os.path.getctime

    for path in Path(base).rglob('*'):
        leaf = True

        try:
            for child in path.iterdir():
                if child.is_dir():
                    leaf = False
                    continue
        except NotADirectoryError:
            continue

        if not [x for x in os.listdir(str(path)) if not x.startswith('.')]:
            continue

        if leaf:
            albums.append(str(path))

    logging.info(f"INDEX Done {time.strftime('%X')}")

    return sorted(albums, key=sort_key, reverse=True)


def mediatype(enc):
    '''
    returns mediatype given encoding
    '''
    for mtype in MEDIATYPES:
        if enc.upper().startswith(mtype):
            return MEDIATYPES[mtype]


def metadata(base, album, single=False):
    '''
    returns metadata for an entire album from the album path,
    or for a single track if single is True
    '''
    out = dict()

    for ind, fpath in enumerate(sorted(Path(album).iterdir())):
        key = str(fpath)
        audio = mutagen.File(fpath)
        encoding = type(audio).__name__
        data = dict()

        if not audio or not hasattr(audio, 'tags'):
            continue

        try:
            data = flat_data(audio)
            data.update(vars(audio.info))
            data['type'] = audio.mime[0]
        except AttributeError:
            raise

        data['encoding'] = encoding
        data['src'] = quote(key.replace(base, '/static/Moo'))

        if 'title' not in data:
            name, _ = os.path.splitext(fpath.name)
            data['title'] = name

        if 'track' not in data:
            data['track'] = ind + 1

        data.update(stat(str(fpath)))

        data['uri'] = fpath.as_uri()

        out[key] = data

        if single is True and data:
            return data

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


def sorted_tracks(meta):
    '''
    returns album metadata as dict with keys sorted by disc and then
    track number
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

    for track in sorted(meta):
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


def tags(base, alkey, track_fname):
    '''
    returns all ID3 tags for a single track from album path as dict
    '''
    for fname in Path(os.path.join(base, alkey)).iterdir():
        if track_fname == str(fname):
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


def top_counts(counts, num=12):
    '''
    returns top <num> counts as list of tuples from dict of counts
    limited by maxcount
    '''
    tmp = list()
    top = OrderedDict()

    for item in counts:
        tmp.append((counts[item], item))

    for item in sorted(tmp, reverse=True):
        top[item[1]] = item[0]
        if len(top) >= num:
            break

    return top


def tracks(fpath):
    '''
    returns a list of tracks from a filepath
    '''
    return [str(x) for x in Path(fpath).iterdir() if x.is_file()]
