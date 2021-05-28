'''
Moo search support
'''

import asyncio
import json
import logging
import os
import time

from pathlib import Path

import mutagen

from Moo.play import lib


def find(base, sindex, terms):
    '''
    returns list of results matching terms given sindex (search index)
    '''
    albums = dict()
    artists = dict()
    tracks = list()

    if not terms:
        return albums, artists, tracks

    for entry in sindex.get('results'):

        alkey = entry[0].replace(base, '')
        entry[0] = alkey

        if len(entry) > 1 and terms.lower() in entry[1].lower():
            if entry[1] not in albums:
                albums[alkey] = entry

        if len(entry) > 2 and terms.lower() in entry[2].lower():
            if entry[2] not in artists:
                artists[entry[2]] = entry

        if len(entry) > 3 and terms.lower() in entry[3].lower():
            tracks.append(entry)

    return albums, artists, tracks


def load_search(filepath):
    '''
    returns search index from file
    '''
    if os.path.exists(filepath):
        with open(filepath) as _:
            return json.loads(_.read())


def search_index(albdex):
    '''
    returns full search index from index of albums
    '''
    count = 0
    out = list()
    
    logging.info('> Moodex {}'.format(len(albdex)))
    
    for path in albdex:  # random.sample(albdex, 250):
    
        for track in lib.tracks(path):
            audio = mutagen.File(str(track))
    
            if not audio:
                continue
    
            tags = audio.tags
    
            def _get(tags, labels):
                for lbl in labels:
                    try:
                        val = tags.get(lbl)
                    except ValueError:
                        pass
                    if val:
                        return val
    
            album = _get(tags, ['ALBUM', 'album', 'TALB', '©alb'])
            artist = _get(tags, ['ARTIST', 'artist', 'TPE1', '©ART'])
            title = _get(tags, ['TITLE', 'title', 'TIT2', '©nam'])
    
            if hasattr(album, 'text'):
                album = album.text
            if hasattr(artist, 'text'):
                artist = artist.text
            if hasattr(title, 'text'):
                title = title.text

            if not title:
                name, ext = os.path.splitext(Path(track).name)
                title = [name]

            tmp = [x[0] for x in (album, artist, title) if x and x[0]]

            tmp.insert(0, path)

            out.append(tmp)
    
        if count and count % 100 == 0:
            logging.info(f"Moodex {count}/{len(albdex)}")
            logging.info(f"[{count}] {tmp}")

        count += 1

    return out
