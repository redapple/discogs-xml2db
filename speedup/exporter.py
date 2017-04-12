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
import os

from docopt import docopt

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
}

class EntityCsvExporter(object):
    """Read a Discogs dump XML file and exports SQL table records as CSV.
    """
    def __init__(self, entity, idir, odir, limit=None, bz2=True, dry_run=False, debug=False):
        self.entity = entity
        self.parser = _parsers[entity]()

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
        for cnt, entity in enumerate(filter(self.validate, self.parser.parse(fp)), start=1):
            self.run_ops(entity, operations)
            if self.limit is not None and cnt > self.limit:
                break
        self.clean_ops(operations)
        return cnt


class LabelExporter(EntityCsvExporter):

    def __init__(self, *args, **kwargs):
        super().__init__('label', *args, **kwargs)

        fields = ['id', 'name', 'contactinfo', 'profile', 'parentLabel', 'data_quality']
        self.actions = (
            ('label.csv',       _write_entity,  [fields]),
            ('label_url.csv',   _write_rows,    ['urls']),
        )

    def validate(self, label):
        if not label.name:
            return False
        return True


class ArtistExporter(EntityCsvExporter):

    def __init__(self, *args, **kwargs):
        super().__init__('artist', *args, **kwargs)

        fields = ['id', 'name', 'realname', 'profile', 'data_quality']
        self.actions = (
            ('artist.csv',                  _write_entity,  [fields]),
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

        fields = ['id', 'title', 'year', 'main_release', 'data_quality']
        artist_fields = ['id', 'anv', 'join', 'role']
        video_fields = ['duration', 'title', 'description', 'src']
        self.actions = (
            ('master.csv',          _write_entity,      [fields]),
            ('master_artist.csv',   _write_fields_rows, ['artists', artist_fields]),
            ('master_video.csv',    _write_fields_rows, ['videos',  video_fields]),
            ('master_genre.csv',    _write_rows,        ['genres']),
            ('master_style.csv',    _write_rows,        ['styles']),

        )

_exporters = {
    'label': LabelExporter,
    'artist': ArtistExporter,
    'master': MasterExporter,
}



def _export_releases(infile, outbase, export_limit=None):
    release_fields = ['id', 'title', 'released', 'country', 'notes', 'data_quality', 'master_id']
    release_artist_fields = [ 'id', 'extra', 'anv', 'join', 'role', 'tracks']
    release_label_fields = [ 'name', 'catno']
    release_video_fields = [ 'duration', 'title', 'description', 'src']
    release_company_fields = [ 'id', 'name', 'entity_type', 'entity_type_name', 'resource_url']
    release_identifier_fields = [ 'description', 'type', 'value']
    release_format_fields = [ 'name', 'qty', 'text', 'descriptions']
    release_track_fields = ['sequence', 'position', 'parent', 'title', 'duration']

    with bz2.open(os.path.join(outbase, 'release.csv.bz2'), 'wt') as f1, \
         bz2.open(os.path.join(outbase, 'release_artist.csv.bz2'), 'wt') as f2, \
         bz2.open(os.path.join(outbase, 'release_label.csv.bz2'), 'wt') as f3, \
         bz2.open(os.path.join(outbase, 'release_genre.csv.bz2'), 'wt') as f4, \
         bz2.open(os.path.join(outbase, 'release_style.csv.bz2'), 'wt') as f5, \
         bz2.open(os.path.join(outbase, 'release_video.csv.bz2'), 'wt') as f6, \
         bz2.open(os.path.join(outbase, 'release_company.csv.bz2'), 'wt') as f7, \
         bz2.open(os.path.join(outbase, 'release_identifier.csv.bz2'), 'wt') as f8, \
         bz2.open(os.path.join(outbase, 'release_format.csv.bz2'), 'wt') as f9, \
         bz2.open(os.path.join(outbase, 'release_track.csv.bz2'), 'wt') as f10, \
         bz2.open(os.path.join(outbase, 'release_track_artist.csv.bz2'), 'wt') as f11:

        releases = csv.writer(f1)
        releases_artists = csv.writer(f2)
        releases_labels = csv.writer(f3)
        releases_genres = csv.writer(f4)
        releases_styles = csv.writer(f5)
        releases_videos = csv.writer(f6)
        releases_companies = csv.writer(f7)
        releases_identifiers = csv.writer(f8)
        releases_formats = csv.writer(f9)
        releases_tracks = csv.writer(f10)
        releases_tracks_artists = csv.writer(f11)

        parser = DiscogsReleaseParser()
        for cnt, release in enumerate(parser.parse(infile), start=1):

            _write_entity(releases, release, release_fields)

            _write_fields_rows(releases_artists, release, 'artists', release_artist_fields)
            _write_fields_rows(releases_artists, release, 'extraartists', release_artist_fields)

            _write_fields_rows(releases_labels, release, 'labels', release_label_fields)
            _write_fields_rows(releases_videos, release, 'videos', release_video_fields)
            _write_fields_rows(releases_formats, release, 'formats', release_format_fields)

            _write_fields_rows(releases_companies, release, 'companies', release_company_fields)
            _write_fields_rows(releases_identifiers, release, 'identifiers', release_identifier_fields)

            _write_rows(releases_genres, release, 'genres')
            _write_rows(releases_styles, release, 'styles')

            _write_fields_rows(releases_tracks, release, 'tracklist', release_track_fields)

            entity = release
            writer = releases_tracks_artists
            writer.writerows(
                [entity.id, track.sequence]
                + [getattr(element, i, '') for i in release_artist_fields]
                for track in getattr(entity, 'tracklist', [])
                for element in getattr(track, 'artists', []) + getattr(track, 'extraartists', [])
            )

            if export_limit is not None and cnt > export_limit:
                break

        print("Wrote %d releases" % cnt)

def export_artists(export_limit=None):
    _export_artists(
        gzip.GzipFile(os.path.join(inbase, 'discogs_{}_artists.xml.gz'.format(dt))),
        outbase,
        export_limit=export_limit)

def export_labels(export_limit=None):
    _export_labels(
        gzip.GzipFile(os.path.join(inbase, 'discogs_{}_labels.xml.gz'.format(dt))),
        outbase,
        export_limit=export_limit)

def export_masters(export_limit=None):
    _export_masters(
        gzip.GzipFile(os.path.join(inbase, 'discogs_{}_masters.xml.gz'.format(dt))),
        outbase,
        export_limit=export_limit)

def export_releases(export_limit=None):
    _export_releases(
        gzip.GzipFile(os.path.join(inbase, 'discogs_{}_releases.xml.gz'.format(dt))),
        outbase,
        export_limit=export_limit)

def main(args):

    arguments = docopt(__doc__, version='Discogs-to-SQL exporter')

    inbase = arguments['INPUT']
    outbase = arguments['OUTPUT'] or '.'
    limit = int(arguments['--limit']) if arguments['--limit'] else None
    bz2_on = arguments['--bz2']
    debug = arguments['--debug']

    for entity in arguments['--export']:
        exporter = _exporters[entity](inbase, outbase, limit=limit, bz2=bz2_on, debug=debug)
        exporter.export()
    #export_labels(inbase, outbase, export_limit)
    #export_artists(inbase, outbase, export_limit)
    #export_masters(inbase, outbase, export_limit)
    #export_releases(inbase, outbase, export_limit)


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
