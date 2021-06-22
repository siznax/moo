'''
MooPlaylists class
'''

import os
import json
import logging


class MooPlaylists:

    '''returns instance of MooPlaylists'''

    shuffle = None

    def __init__(self, fname):
        self.fname = fname

        logging.basicConfig(level=logging.INFO)

        if os.path.exists(fname):
            self.lists = self.get()
        else:
            self.lists = dict()

        self.shuffle = dict()

    def delete(self, name):
        '''
        delete playlist with name and save playlists
        '''
        if name in self.lists:
            del self.lists[name]
            self.save()

    def get(self):
        '''
        read playlists from file
        '''
        with open(self.fname) as _:
            data = _.read()
            logging.info('Read %d bytes from %s', _.tell(), self.fname)
            return json.loads(data)

    def move(self, position, name, data):
        '''
        move data in playlist with name to position
        '''
        dest = position - 1

        if dest < 0:
            dest = len(self.lists[name]) - 1

        if dest > len(self.lists[name]) - 1:
            dest = 0

        self.lists[name].remove(data)
        self.lists[name].insert(dest, data)
        self.save()

    def put(self, name, data):
        '''
        append data (dict) to list with name and save playlists
        '''
        logging.info('PUT %s %s', name, data)

        if not name or not data:
            return

        if name not in self.lists:
            self.lists[name] = list()

        if data not in self.lists[name]:
            self.lists[name].append(data)
            self.save()

    def remove(self, name, data):
        '''
        remove data (dict) from playlist with name and save playlists
        '''
        logging.info('REMOVE %s %s', name, data)

        if data in self.lists[name]:
            self.lists[name].remove(data)
            self.save()
        else:
            raise ValueError

        if len(self.lists[name]) == 0:
            self.delete(name)

    def rename(self, old, new):
        '''
        rename playlist from old to new
        '''
        if old in self.lists:
            self.lists[new] = self.lists.pop(old)
            self.save()

    def save(self):
        '''
        save playlists to file
        '''
        with open(self.fname, 'w') as _:
            _.write(json.dumps(self.lists))
            logging.info('Wrote %d bytes to %s', _.tell(), self.fname)

    def template_data(self, moo, name, index):
        '''
        return data to render play (playlist) template
        '''
        track = self.lists[name][index - 1]

        parts = track['source'].split('/')
        alkey = '/' + '/'.join(parts[2:])
        path = os.path.join(moo.base, alkey[1:])
        aldata = moo.metadata(path)

        tnum = int(parts[1])
        tind = int(tnum) - 1
        dkey = sorted(aldata.keys())[tind]
        data = aldata[dkey]

        return {
            'alkey': alkey,
            'data': data,
            'track': track}
