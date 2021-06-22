'''
MooAlbums class
'''

import logging
import os
import time

from collections import Counter, OrderedDict
from pathlib import Path
from urllib.parse import quote

import mutagen

from .tags import mp3_fields, mp4_fields


class MooAlbums:

    '''
    returns an instance of MooAlbums
    '''

    index = list()
    albums = dict()

    def __init__(self, config):
        logging.basicConfig(level=logging.INFO)

        self.base = config.get('BASE')

        if self.base and os.path.exists(self.base):
            self.index = self.albums_index()
            self.albums = self.albums_data()
            self.alpha = self.albums_alpha()

    def albums_alpha(self, mtag='artist'):
        '''
        returns a map of letters and counts from selected mtag
        '''
        letters = Counter()

        for path in self.albums:
            alb = self.albums[path]
            tag = alb.get(mtag)
            if tag:
                letters[tag[0].upper()] += 1

        return dict(letters)

    def albums_data(self):
        '''
        returns dict of minimal album metadata
        '''
        logging.info("Getting ALBUMS %s", time.strftime('%X'))

        start = time.time()
        out = dict()

        for path in self.index:
            pobj = Path(path)
            meta = self.metadata(pobj, True)

            if not meta.get('album'):
                continue  # index, albums diverge

            artist = meta.get('album_artist') or meta.get('artist')

            pruned = {
                'album': meta.get('album'),
                'artist': artist.split(';')[0] if artist else 'None',
                'encoding': meta.get('encoding'),
                'genre': meta.get('genre') or 'None',
                'mtime': meta.get('mtime', 0),
                'year': meta['year'][:4] if meta.get('year') else 'None'}

            out[path] = pruned

        self.index = list(out.keys())  # index, albums in sync

        logging.info('ALBUMS Done %s (%d seconds)',
                     time.strftime('%X'),
                     int(time.time() - start))

        return out

    def albums_index(self, sort=None):
        '''
        returns list of paths that do not contain directories,
        reverse-sorted by mtime (default), 'atime', or 'ctime'
        '''
        logging.info('Computing INDEX %s', time.strftime('%X'))

        start = time.time()
        albums = list()  # paths that do not contain directories
        sort_key = os.path.getmtime

        if sort:
            if sort == 'atime':
                sort_key = os.path.getatime
            if sort == 'ctime':
                sort_key = os.path.getctime

        for path in Path(self.base).rglob('*'):
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

        logging.info('INDEX Done %s (%d seconds)',
                     time.strftime('%X'),
                     int(time.time() - start))

        return sorted(albums, key=sort_key, reverse=True)

    def metadata(self, album, single=False, track=None):
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
                # hmmm
                raise

            data['encoding'] = encoding
            data['src'] = quote(key.replace(self.base, '/static/Moo'))

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
        tracks = sorted_tracks(out)

        if track:
            for num, item in enumerate(sorted(tracks)):
                if num + 1 == track:
                    return tracks[item]

        return tracks

    def sorted_albums(self, sort_key, reverse=False):
        '''
        return OrderedDict of albums sorted by sort_key
        '''
        tmp = list()
        nones = list()
        out = OrderedDict()

        for item in self.albums:
            facet = self.albums[item].get(sort_key)
            data = self.albums[item]

            if facet == 'None':
                nones.append((facet, item, data))
            else:
                tmp.append((facet, item, data))

        for tup in sorted(tmp, reverse=reverse):
            out[tup[1]] = tup[2]

        for tup in nones:
            out[tup[1]] = tup[2]

        return out

    def sort_subset(self, sub, sort_key, reverse=False):
        '''
        returns OrderedDict of a subset of albums sorted by sort_key
        '''
        tmp = list()
        out = OrderedDict()

        for path in sub:
            tmp.append((sub[path].get(sort_key), path))

        for item in sorted(tmp, reverse=reverse):
            out[item[1]] = self.albums.get(item[1])

        return out

    def subset(self, facet, value, sort_key=None, reverse=False):
        '''
        returns dict of albums filtered by metadata <facet> containing
        <value> and sorted by sort_key. The sort order will be
        reversed if reverse is True.
        '''
        sub = dict()

        for alb in self.albums:

            if value == 'None' and not self.albums[alb][facet]:
                sub[alb] = self.albums[alb]
                continue

            if value.lower() in self.albums[alb][facet].lower():
                sub[alb] = self.albums[alb]

        if sort_key:
            tmp = list()
            non = list()
            alb = OrderedDict()

            for path in sub:

                # tuple of (sort-key-value, path)
                val = sub[path].get(sort_key)

                if val == 'None':
                    non.append(('None', path))
                else:
                    tmp.append((val, path))

            for item in sorted(tmp, reverse=reverse):
                alb[item[1]] = sub[item[1]]

            for item in sorted(non, reverse=reverse):
                alb[item[1]] = sub[item[1]]

            return alb

        return sub


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

    return None


def parse_fnames(mdata):
    '''
    need to review what this does...
    '''
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


def rekey_catchall(tags):
    '''
    rekey tag fields not defined by mp3_tags or mp4_tags
    '''
    fields = {
        'discnumber': 'disc',
        'tracknumber': 'track',
    }

    _ = dict()

    for item in tags:
        if item in fields:
            key = fields.get(item)
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

            return str(text)

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
    '''
    returns file stat data as dict
    '''
    ostat = os.stat(fpath)

    return {
        'fpath': fpath,
        'atime': ostat.st_atime,
        'mtime': ostat.st_mtime,
        'size': ostat.st_size}


def tracks(fpath):
    '''
    returns a list of tracks from a filepath
    '''
    return [str(x) for x in Path(fpath).iterdir() if x.is_file()]
