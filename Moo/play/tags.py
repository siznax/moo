'''
Moo Tag Fields
~~~~~~~~~~~~~~
'''


# https://id3.org/id3v2.4.0-frames

mp3_fields = {
    'APIC': 'APIC',
    'COMM': 'comments',
    'COMM::eng': 'URL',
    'COMM::XXX': 'URL',
    'LINK': 'link',
    'MCDI': 'identifier',
    'PCNT': 'play-count',
    'SYLT': 'lyrics-synchronised',
    'TALB': 'album',
    'TBPM': 'bpm',
    'TCOM': 'composer',
    'TCON': 'genre',
    'TCOP': 'copyright',
    'TDRC': 'year',
    'TENC': 'encoder',
    'TEXT': 'lyricist',
    'TFLT': 'file-type',
    'TIPL': 'personnel',
    'TIT1': 'group',
    'TIT2': 'title',
    'TIT3': 'subtitle',
    'TLAN': 'language',
    'TLEN': 'length',
    'TMCL': 'credits',
    'TMED': 'mediatype',
    'TMOO': 'mood',
    'TPE1': 'artist',
    'TPE2': 'album_artist',
    'TPE3': 'conductor',
    'TPE4': 'remix',
    'TPOS': 'disc',
    'TPUB': 'publisher',
    'TRCK': 'track',
    'TRSN': 'radio',
    'TRSO': 'owner',
    'TSSE': 'encoding',
    'TSST': 'set-subtitle',
    'TXXX': 'info',
    'USER': 'terms',
    'USLT': 'lyrics',
    'WCOM': 'commercial',
    'WCOP': 'copyright',
    'WOAF': 'audio-file-url',
    'WOAR': 'artist-url',
    'WOAS': 'audio-source-url',
    'WORS': 'radio-url',
    'WPUB': 'publisher-url',
    'WXXX': 'URL',
    # mutagen.flac.VCFLACDict()
    'ALBUM': 'album',
    'ARTIST': 'artist',
    'TITLE': 'title',
    'DATE': 'year',
    'GENRE': 'genre',
    'album': 'album',
    'artist': 'artist',
    'title': 'title',
    'date': 'year',
    'genre': 'genre',
    # /mutagen.flac.VCFLACDict()
}


# https://mutagen.readthedocs.io/en/latest/api/mp4.html#mutagen.mp4.MP4Tags

mp4_fields = {
    '\xa9ART': 'artist',
    '\xa9alb': 'album',
    '\xa9cmt': 'comment',
    '\xa9day': 'year',
    '\xa9gen': 'genre',
    '\xa9mvc': 'movement-count',
    '\xa9mvi': 'movement-index',
    '\xa9nam': 'title',
    '\xa9too': 'encoder',
    '\xa9wrt': 'composer',
    'aART': 'album_artist',
    'rtng': 'rating',
    'shwm': 'movement',
    'stik': 'media-kind',
    'trkn': 'track',
}
