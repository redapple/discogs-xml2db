# -*- coding: utf-8 -*-
import bz2
import csv
import os

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


dt = '20170301'
inbase = '/home/paul/dl/discogs/{}/'.format(dt)
outbase = '.'

export_limit = None
#export_limit = 100000


def _export_labels(infile, outbase, export_limit=None):
    label_fields = ['id', 'name', 'contactinfo', 'profile', 'parentLabel', 'data_quality']

    with bz2.open(os.path.join(outbase, 'label.csv.bz2'), 'wt', encoding='utf-8') as f1, \
         bz2.open(os.path.join(outbase, 'label_url.csv.bz2'), 'wt', encoding='utf-8') as f2:
        labels = csv.writer(f1)
        labels_urls = csv.writer(f2)

        parser = DiscogsLabelParser()
        for cnt, label in enumerate(parser.parse(infile), start=1):
            if not label.name:
                continue
            _write_entity(labels, label, label_fields)
            _write_rows(labels_urls, label, 'urls')

            if export_limit is not None and cnt > export_limit:
                break

        print("Wrote %d labels" % cnt)


def _export_artists(infile, outbase, export_limit=None):
    artist_fields = ['id', 'name', 'realname', 'profile', 'data_quality']

    with bz2.open(os.path.join(outbase, 'artist.csv.bz2'), 'wt', encoding='utf-8') as f1, \
         bz2.open(os.path.join(outbase, 'artist_alias.csv.bz2'), 'wt', encoding='utf-8') as f2, \
         bz2.open(os.path.join(outbase, 'artist_namevariation.csv.bz2'), 'wt', encoding='utf-8') as f3, \
         bz2.open(os.path.join(outbase, 'group_member.csv.bz2'), 'wt', encoding='utf-8') as f4, \
         bz2.open(os.path.join(outbase, 'artist_url.csv.bz2'), 'wt', encoding='utf-8') as f5:

        artists = csv.writer(f1)
        artists_aliases = csv.writer(f2)
        artists_variations = csv.writer(f3)
        groups_members = csv.writer(f4)
        artists_urls = csv.writer(f5)

        parser = DiscogsArtistParser()
        for cnt, artist in enumerate(parser.parse(infile), start=1):
            if not artist.name:
                artist.name = '[artist #%d]' % artist.id

            _write_entity(artists, artist, artist_fields)
            _write_rows(artists_aliases, artist, 'aliases')
            _write_rows(artists_variations, artist, 'namevariations')
            _write_rows(artists_urls, artist, 'urls')

            groups_members.writerows([[artist.id, member_id, member_name]
                                     for member_id, member_name in getattr(artist, 'members', [])])

            if export_limit is not None and cnt > export_limit:
                break

        print("Wrote %d artists" % cnt)


def _export_masters(infile, outbase, export_limit=None):
    master_fields = ['id', 'title', 'year', 'main_release', 'data_quality']
    master_artist_fields = ['id', 'anv', 'join', 'role']
    master_video_fields = ['duration', 'title', 'description', 'src']

    with bz2.open(os.path.join(outbase, 'master.csv.bz2'), 'wt', encoding='utf-8') as f1, \
         bz2.open(os.path.join(outbase, 'master_artist.csv.bz2'), 'wt', encoding='utf-8') as f2, \
         bz2.open(os.path.join(outbase, 'master_video.csv.bz2'), 'wt', encoding='utf-8') as f3, \
         bz2.open(os.path.join(outbase, 'master_genre.csv.bz2'), 'wt', encoding='utf-8') as f4, \
         bz2.open(os.path.join(outbase, 'master_style.csv.bz2'), 'wt', encoding='utf-8') as f5:

        masters = csv.writer(f1)
        masters_artists = csv.writer(f2)
        masters_videos = csv.writer(f3)
        masters_genres = csv.writer(f4)
        masters_styles = csv.writer(f5)

        parser = DiscogsMasterParser()
        for cnt, master in enumerate(parser.parse(infile), start=1):

            _write_entity(masters, master, master_fields)
            _write_fields_rows(masters_artists, master, 'artists', master_artist_fields)
            _write_fields_rows(masters_videos, master, 'videos', master_video_fields)
            _write_rows(masters_genres, master, 'genres')
            _write_rows(masters_styles, master, 'styles')

            if export_limit is not None and cnt > export_limit:
                break

        print("Wrote %d masters" % cnt)


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
    export_labels(export_limit)
    export_artists(export_limit)
    export_masters(export_limit)
    export_releases(export_limit)


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
