# -*- coding: utf-8 -*-
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


dt = '20170201'
base = '/home/paul/dl/discogs/{}/'.format(dt)
export_limit = True


def export_labels():
    label_fields = ['id', 'name', 'contactinfo', 'profile', 'parentLabel', 'data_quality']

    with open(os.path.join(base, 'discogs.labels.csv'), 'w') as f1, \
         open(os.path.join(base, 'discogs.labels_urls.csv'), 'w') as f2:
        labels = csv.writer(f1)
        labels_urls = csv.writer(f2)

        parser = DiscogsLabelParser()
        for cnt, label in enumerate(
                parser.parse(os.path.join(base,'discogs_{}_labels.xml.gz'.format(dt))),
                start=1):
            if not label.name:
                continue
            _write_entity(labels, label, label_fields)
            _write_rows(labels_urls, label, 'urls')

            if export_limit and cnt > 100:
                break

        print("Wrote %d labels" % cnt)


def export_artists():
    artist_fields = ['id', 'name', 'realname', 'profile', 'data_quality']

    with open(os.path.join(base, 'discogs.artists.csv'), 'w') as f1, \
         open(os.path.join(base, 'discogs.artists_aliases.csv'), 'w') as f2, \
         open(os.path.join(base, 'discogs.artists_variations.csv'), 'w') as f3, \
         open(os.path.join(base, 'discogs.groups_members.csv'), 'w') as f4, \
         open(os.path.join(base, 'discogs.artists_urls.csv'), 'w') as f5:

        artists = csv.writer(f1)
        artists_aliases = csv.writer(f2)
        artists_variations = csv.writer(f3)
        groups_members = csv.writer(f4)
        artists_urls = csv.writer(f5)

        parser = DiscogsArtistParser()
        for cnt, artist in enumerate(
                parser.parse(os.path.join(base, 'discogs_{}_artists.xml.gz'.format(dt))),
                start=1):
            if not artist.name:
                continue

            _write_entity(artists, artist, artist_fields)
            _write_rows(artists_aliases, artist, 'aliases')
            _write_rows(artists_variations, artist, 'namevariations')
            _write_rows(artists_urls, artist, 'urls')

            groups_members.writerows([[artist.id, member_id, member_name]
                                     for member_id, member_name in getattr(artist, 'members', [])])
            if export_limit and cnt > 100:
                break

        print("Wrote %d artists" % cnt)


def export_masters():
    master_fields = ['id', 'title', 'year', 'main_release', 'data_quality']
    master_artist_fields = ['id', 'anv', 'join', 'role']
    master_video_fields = ['duration', 'title', 'description', 'src']

    with open(os.path.join(base, 'discogs.masters.csv'), 'w') as f1, \
         open(os.path.join(base, 'discogs.masters_artists.csv'), 'w') as f2, \
         open(os.path.join(base, 'discogs.masters_videos.csv'), 'w') as f3, \
         open(os.path.join(base, 'discogs.masters_genres.csv'), 'w') as f4, \
         open(os.path.join(base, 'discogs.masters_styles.csv'), 'w') as f5:

        masters = csv.writer(f1)
        masters_artists = csv.writer(f2)
        masters_videos = csv.writer(f3)
        masters_genres = csv.writer(f4)
        masters_styles = csv.writer(f5)

        parser = DiscogsMasterParser()
        for cnt, master in enumerate(
                parser.parse(os.path.join(base, 'discogs_{}_masters.xml.gz'.format(dt))),
                start=1):

            _write_entity(masters, master, master_fields)
            _write_fields_rows(masters_artists, master, 'artists', master_artist_fields)
            _write_fields_rows(masters_videos, master, 'videos', master_video_fields)
            _write_rows(masters_genres, master, 'genres')
            _write_rows(masters_styles, master, 'styles')

            if export_limit and cnt > 100:
                break

        print("Wrote %d masters" % cnt)


def main(args):
    export_labels()
    export_artists()
    export_masters()


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
