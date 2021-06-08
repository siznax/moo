'''
MooSearch class
'''

import json
import logging
import os

from pathlib import Path

import mutagen

from Moo.play import albums


class MooSearch:

    '''
    instance of MooSearch
    '''

    def __init__(self, config):
        self.base = config.get('BASE')
        self.indexfile = config.get('SINDEX')
        self.index = MooSearch.load_search(self.indexfile)

    def find(self, terms):
        '''
        returns list of results matching terms given sindex (search index)
        '''
        alb = dict()
        art = dict()
        trk = list()

        if not terms:
            return alb, art, trk

        for entry in self.index.get('results'):

            entry[0] = entry[0].replace(self.base, '')  # path
            terms = terms.lower()

            if isinstance(entry[1], str) and terms in entry[1].lower():
                alb[entry[0]] = entry

            if isinstance(entry[2], str) and terms in entry[2].lower():
                art[entry[2]] = entry

            if isinstance(entry[3], str) and terms in entry[3].lower():
                trk.append(entry)

        return alb, art, trk

    @staticmethod
    def load_search(fpath):
        '''
        returns search index from file
        '''
        if os.path.exists(fpath):
            with open(fpath) as _:
                data = json.loads(_.read())
                logging.info('Read search index: %s (%d bytes)',
                             fpath, _.tell())
                return data

        return None

    @staticmethod
    def search_index(albdex, limit=None):
        '''
        returns full search index from index of albums
        '''
        count = 0
        out = list()

        logging.info('> Moodex %s', len(albdex))

        for path in albdex:  # random.sample(albdex, 250):

            for ind, track in enumerate(sorted(albums.tracks(path))):
                audio = mutagen.File(str(track))

                if not audio:
                    continue

                album = get(audio.tags, ['ALBUM', 'album', 'TALB', '©alb'])
                artist = get(audio.tags, ['ARTIST', 'artist', 'TPE1', '©ART'])
                title = get(audio.tags, ['TITLE', 'title', 'TIT2', '©nam'])
                tnum = get(audio.tags, ['TRCK', 'track', 'trkn'])

                if not title:
                    fname, _ = os.path.splitext(Path(track).name)
                    title = fname

                try:
                    ind = int(tnum) - 1
                except (TypeError, ValueError):
                    pass

                tmp = [path, album, artist, title, ind + 1]

                out.append(tmp)

            if count and count % 100 == 0:
                logging.info('Moodex %d/%d', count, len(albdex))
                logging.info('[%d] %s', count, tmp)

            count += 1

            if limit and len(out) >= limit:
                return out

        return out


def get(tags, labels):
    '''return value for label from tags'''
    for lbl in labels:

        try:
            val = tags.get(lbl)
        except ValueError:
            pass

        if val:
            if hasattr(val, 'text'):
                val = val.text

            if isinstance(val, list):
                val = val[0]

            return val

    return None
