# -*- coding: utf-8 -*-
"""Usage: exporter.py [--bz2] [--limit=<lines>] [--debug] INPUT [OUTPUT] [--export=<entity>]...

Options:
  --bz2                 Compress output files using bz2 compression library.
  --limit=<lines>       Limit export to some number of entities
  --export=<entity>     Limit export to some entities (repeatable)
  --debug               Turn on debugging prints

"""
import bz2
import csv
import glob
import gzip
import os

from docopt import docopt
import requests
from tqdm import tqdm


from parser import *


def _write_entity(writer, entity, fields):
    writer.writerow([getattr(entity, i, '') for i in fields])

def _write_fields_rows(writer, entity, name, fields):
    writer.writerows(
            [entity.id] + [getattr(element, i, '') for i in fields]
            for element in getattr(entity, name, [])
        )
def _write_rows(writer, entity, name):
    writer.writerows(
            [entity.id, element]
            for element in getattr(entity, name, [])
            if element
        )


_parsers = {
    'artist': DiscogsArtistParser,
    'label': DiscogsLabelParser,
    'master': DiscogsMasterParser,
    'release': DiscogsReleaseParser,
}

class EntityCsvExporter(object):
    """Read a Discogs dump XML file and exports SQL table records as CSV.
    """
    def __init__(self, entity, idir, odir, limit=None, bz2=True,
                 dry_run=False, debug=False, max_hint=None, verbose=False):
        self.entity = entity
        self.parser = _parsers[entity]()
        self.max_hint = max_hint
        self.verbose = verbose

        lookup = 'discogs_[0-9]*_{}s.xml*'.format(entity)
        self.pattern = os.path.join(idir, lookup)

        # where and how the exporter will write to
        self.odir = odir
        self.limit = limit
        self.bz2 = bz2
        self.dry_run = dry_run

        self.debug = debug

    def openfile(self):
        for fpath in glob.glob(self.pattern):
            if fpath.endswith('.gz'):
                return gzip.GzipFile(fpath)
            elif fpath.endswith('.xml'):
                return open(fpath)
            else:
                raise RuntimeError('unknown file type: {}'.format(fpath))

    def export(self):
        return self.export_from_file(self.openfile())

    @staticmethod
    def validate(entity):
        return True

    def build_ops(self):
        openf = bz2.open if self.bz2 else open
        outf = '{}.bz2' if self.bz2 else '{}'

        operations = []
        for out, fn, args in self.actions:
            outfp = openf(os.path.join(self.odir, outf.format(out)), 'wt', encoding='utf-8')
            writer = csv.writer(outfp)
            operations.append(
                (writer, fn, args, outfp)
            )
        return operations

    def run_ops(self, entity, operations):
        if self.dry_run:
            return
        for writer, f, args, _ in operations:
            if args is not None:
                f(writer, entity, *args)
            else:
                f(writer, entity)

    def clean_ops(self, operations):
        if self.dry_run:
            return
        for _, _, _, fp in operations:
            fp.close()

    def export_from_file(self, fp):
        operations = self.build_ops()
        with tqdm(total=self.max_hint, ncols=80,
                  desc='Processing {}s'.format(self.entity),
                  unit='{}s'.format(self.entity)) as pbar:
            for cnt, entity in enumerate(filter(self.validate, self.parser.parse(fp)), start=1):
                self.run_ops(entity, operations)
                pbar.update()
                if self.limit is not None and cnt >= self.limit:
                    break
        self.clean_ops(operations)
        return cnt


class LabelExporter(EntityCsvExporter):

    def __init__(self, *args, **kwargs):
        super().__init__('label', *args, **kwargs)

        main_fields = ['id', 'name', 'contactinfo', 'profile', 'parentLabel', 'data_quality']
        self.actions = (
            ('label.csv',       _write_entity,  [main_fields]),
            ('label_url.csv',   _write_rows,    ['urls']),
        )

    def validate(self, label):
        if not label.name:
            return False
        return True


class ArtistExporter(EntityCsvExporter):

    def __init__(self, *args, **kwargs):
        super().__init__('artist', *args, **kwargs)

        main_fields = ['id', 'name', 'realname', 'profile', 'data_quality']
        self.actions = (
            ('artist.csv',                  _write_entity,  [main_fields]),
            ('artist_alias.csv',            _write_rows,    ['aliases']),
            ('artist_namevariation.csv',    _write_rows,    ['namevariations']),
            ('artist_url.csv',              _write_rows,    ['urls']),
            ('group_member.csv',            self.write_group_members,  None),
        )

    @staticmethod
    def write_group_members(writer, artist):
        writer.writerows([
            [artist.id, member_id, member_name]
            for member_id, member_name in getattr(artist, 'members', [])
        ])

    def validate(self, artist):
        if not artist.name:
            artist.name = '[artist #%d]' % artist.id
        return True


class MasterExporter(EntityCsvExporter):

    def __init__(self, *args, **kwargs):
        super().__init__('master', *args, **kwargs)

        main_fields = ['id', 'title', 'year', 'main_release', 'data_quality']
        artist_fields = ['id', 'anv', 'join', 'role']
        video_fields = ['duration', 'title', 'description', 'src']
        self.actions = (
            ('master.csv',          _write_entity,      [main_fields]),
            ('master_artist.csv',   _write_fields_rows, ['artists', artist_fields]),
            ('master_video.csv',    _write_fields_rows, ['videos',  video_fields]),
            ('master_genre.csv',    _write_rows,        ['genres']),
            ('master_style.csv',    _write_rows,        ['styles']),

        )


class ReleaseExporter(EntityCsvExporter):

    def __init__(self, *args, **kwargs):
        super().__init__('release', *args, **kwargs)

        main_fields = ['id', 'title', 'released', 'country', 'notes', 'data_quality', 'master_id']
        label_fields = [ 'name', 'catno']
        video_fields = [ 'duration', 'title', 'description', 'src']
        format_fields = [ 'name', 'qty', 'text', 'descriptions']
        company_fields = [ 'id', 'name', 'entity_type', 'entity_type_name', 'resource_url']
        identifier_fields = [ 'description', 'type', 'value']
        track_fields = ['sequence', 'position', 'parent', 'title', 'duration']

        self.artist_fields = [ 'id', 'extra', 'anv', 'join', 'role', 'tracks']

        self.actions = (
            ('release.csv',             _write_entity,      [main_fields]),
            ('release_genre.csv',       _write_rows,        ['genres']),
            ('release_style.csv',       _write_rows,        ['styles']),
            ('release_label.csv',       _write_fields_rows, ['labels',      label_fields]),
            ('release_video.csv',       _write_fields_rows, ['videos',      video_fields]),
            ('release_format.csv',      _write_fields_rows, ['formats',     format_fields]),
            ('release_company.csv',     _write_fields_rows, ['companies',   company_fields]),
            ('release_identifier.csv',  _write_fields_rows, ['identifiers', identifier_fields]),
            ('release_track.csv',       _write_fields_rows, ['tracklist',   track_fields]),

            # Two special operations
            ('release_artist.csv',          self.write_artists, None),
            ('release_track_artist.csv',    self.write_track_artists, None),
        )

    def write_artists(self, writer, release):
        _write_fields_rows(writer, release, 'artists', self.artist_fields)
        _write_fields_rows(writer, release, 'extraartists', self.artist_fields)

    def write_track_artists(self, writer, release):
        writer.writerows(
            ([release.id, track.sequence] +
             [getattr(element, i, '') for i in self.artist_fields])
            for track in getattr(release, 'tracklist', [])
                for element in (getattr(track, 'artists', []) +
                                getattr(track, 'extraartists', []))
        )


_exporters = {
    'label': LabelExporter,
    'artist': ArtistExporter,
    'master': MasterExporter,
    'release': ReleaseExporter,
}


def main(args):

    arguments = docopt(__doc__, version='Discogs-to-SQL exporter')

    inbase = arguments['INPUT']
    outbase = arguments['OUTPUT'] or '.'
    limit = int(arguments['--limit']) if arguments['--limit'] else None
    bz2_on = arguments['--bz2']
    debug = arguments['--debug']

    rough_counts = {
        'artists':  5000000,
        'labels':   1100000,
        'masters':  1200000,
        'releases': 8500000,
    }
    r = requests.get('https://api.discogs.com/', timeout=5)
    try:
        rough_counts.update(r.json().get('statistics'))
    except:
        pass

    for entity in arguments['--export']:
        expected_count = rough_counts['{}s'.format(entity)]
        exporter = _exporters[entity](inbase, outbase, limit=limit, bz2=bz2_on,
            debug=debug, max_hint=min(expected_count, limit or expected_count))
        exporter.export()

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
