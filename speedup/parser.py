# -*- coding: utf-8 -*-
import gzip
import collections
from itertools import zip_longest

import lxml.etree as lxml_etree

from entities import *


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


class DiscogsDumpEntityParser(object):

    entity_tag = None

    def entity_id(self, element):
        i = element.find('id')
        if i is not None:
            return int(i.text)

    def parse(self, filename):
        with gzip.GzipFile(filename) as f:
            for event, element in lxml_etree.iterparse(f, tag=self.entity_tag):
                i = self.entity_id(element)
                if i is not None:
                    yield self.build_entity(i, element)
                    element.clear()
                    # Also eliminate now-empty references from the root node to elem
                    for ancestor in element.xpath('ancestor-or-self::*'):
                        while ancestor.getprevious() is not None:
                            del ancestor.getparent()[0]

    def build_entity(self, entity_id, element):
        raise NotImplementedError

    def children_text(self, element):
        for child in element.iterchildren():
            yield child.text

    def element_attributes(self, element, entity_class):
        for child in element.iterchildren():
            entity = entity_class()
            for k, v in child.attrib.items():
                setattr(entity, k, v)
            yield entity


class DiscogsArtistParser(DiscogsDumpEntityParser):

    entity_tag = "artist"

    #<members><id>26</id><name>Alexi Delano</name><id>27</id><name>Cari Lekebusch</name></members>
    def element_members(self, element):
        for id, name in grouper([child.text for child in element.iterchildren()], 2):
            yield int(id), name

    def build_entity(self, entity_id, element):
        artist = Artist()
        artist.id = entity_id
        for e in element.iterchildren():
            t = e.tag
            if t in ('data_quality',
                     'name',
                     'realname',
                     'profile'):
                setattr(artist, t, e.text)

            # <aliases><name>some name</name>...
            # <namevariations><name>some name</name>...
            # <groups><name>some name</name>...
            # <urls><url>http://www.joshwink.com/</url>...
            elif t in ('aliases',
                       'namevariations',
                       'groups',
                       'urls'):
                setattr(artist, t, list(self.children_text(e)))

            # --- images don't seem to bring much information
            #elif t in ('images',):
            #    setattr(artist, t, list(self.element_attributes(e, ImageInfo)))

            elif t == 'members':
                setattr(artist, t, list(self.element_members(e)))

        return artist


class DiscogsLabelParser(DiscogsDumpEntityParser):

    entity_tag = "label"

    def build_entity(self, entity_id, element):
        label = Label()
        label.id = entity_id
        for e in element.iterchildren():
            t = e.tag
            if t in ('data_quality',
                     'contactinfo',
                     'name',
                     'profile',
                     'parentLabel'):
                setattr(label, t, e.text)

            elif t in ('sublabels',
                     'urls'):
                setattr(label, t, list(self.children_text(e)))

            elif t in ('images'):
                setattr(label, t, list(self.element_attributes(e, ImageInfo)))
        return label


class DiscogsMasterParser(DiscogsDumpEntityParser):

    entity_tag = "master"

    # <master id="18500"><main_release>155102</main_release>
    def entity_id(self, element):
        i = element.get('id')
        if i is not None:
            return int(i)

    def element_artists(self, element):
        for child in element.iterchildren():
            artist = MasterArtist()
            for e in child.iterchildren():
                t = e.tag
                if t in ('id',):
                    setattr(artist, t, int(e.text))

                elif t in ('name','anv', 'join', 'role'):
                    setattr(artist, t, e.text)
            yield artist

    def element_videos(self, element):
        for child in element.iterchildren():
            entity = Video()

            for e in child.iterchildren():
                t = e.tag
                if t in ('title','description'):
                    setattr(entity, t, e.text)

            for k, v in child.attrib.items():
                if k in ('duration',):
                    setattr(entity, k, int(v))
                elif k in ('src',):
                    setattr(entity, k, v)

            yield entity

    def build_entity(self, entity_id, element):
        master = Master()
        master.id = entity_id
        for e in element.iterchildren():
            t = e.tag
            if t in ('main_release', 'year',):
                setattr(master, t, int(e.text))

            elif t in ('title', 'data_quality', 'notes'):
                setattr(master, t, e.text)

            elif t in ('genres', 'styles',):
                setattr(master, t, list(self.children_text(e)))

            elif t in ('images'):
                setattr(master, t, list(self.element_attributes(e, ImageInfo)))

            elif t in ('artists'):
                setattr(master, t, list(self.element_artists(e)))

            elif t in ('videos'):
                setattr(master, t, list(self.element_videos(e)))
        return master


class DiscogsReleaseParser(DiscogsDumpEntityParser):

    entity_tag = "release"

    def entity_id(self, element):
        i = element.get('id')
        if i is not None:
            return int(i)

    def element_artists(self, element, extra=False):
        for child in element.iterchildren():
            artist = ReleaseArtist()
            artist.extra = extra
            for e in child.iterchildren():
                t = e.tag
                if t in ('id',):
                    setattr(artist, t, int(e.text))

                elif t in ('name','anv', 'join', 'role'):
                    setattr(artist, t, e.text)
            yield artist

    def element_labels(self, element):
        for child in element.iterchildren():
            entity = ReleaseLabel()
            for k, v in child.attrib.items():
                if k in ('catno', 'name'):
                    setattr(entity, k, v)
            yield entity

    def element_videos(self, element):
        for child in element.iterchildren():
            entity = Video()
            for e in child.iterchildren():
                t = e.tag
                if t in ('title','description'):
                    setattr(entity, t, e.text)
            for k, v in child.attrib.items():
                if k in ('duration',):
                    setattr(entity, k, int(v))
                elif k in ('src',):
                    setattr(entity, k, v)
            yield entity

    def element_formats(self, element):
        for child in element.iterchildren():
            entity = ReleaseFormat()
            for e in child.iterchildren():
                t = e.tag
                if t in ('descriptions'):
                    setattr(entity, t, list(self.children_text(e)))

            for k, v in child.attrib.items():
                if k in ('qty',):
                    setattr(entity, k, int(v))
                elif k in ('name', 'text'):
                    setattr(entity, k, v)
            yield entity

    def element_tracklist(self, element):
        for track in element.iterchildren():
            entity = ReleaseTrack()
            for e in track.iterchildren():
                t = e.tag
                if t in ('position', 'title', 'duration'):
                    setattr(entity, t, e.text)
                elif t in ('artists', 'extraartists'):
                    setattr(entity, t,
                            list(self.element_artists(e,
                                                      extra=(t=='extraartists'))))
            yield entity

    def element_identifiers(self, element):
        for child in element.iterchildren():
            entity = ReleaseIdentifier()
            for k, v in child.attrib.items():
                if k in ('description', 'type', 'value'):
                    setattr(entity, k, v)
            yield entity

    def element_companies(self, element):
        for child in element.iterchildren():
            entity = ReleaseCompany()
            for e in child.iterchildren():
                t = e.tag
                if t in ('id', 'entity_type'):
                    setattr(entity, t, int(e.text))

                elif t in ('name','entity_type_name', 'catno', 'resource_url'):
                    setattr(entity, t, e.text)
            yield entity

    def build_entity(self, entity_id, element):
        release = Release()
        release.id = entity_id
        for e in element.iterchildren():
            t = e.tag
            if t in ('master_id',):
                setattr(release, t, int(e.text))

            elif t in ('title', 'country', 'released', 'notes', 'data_quality'):
                setattr(release, t, e.text)

            elif t in ('genres', 'styles',):
                setattr(release, t, list(self.children_text(e)))

            elif t in ('images'):
                setattr(release, t, list(self.element_attributes(e, ImageInfo)))

            elif t in ('artists', 'extraartists'):
                setattr(release, t,
                        list(self.element_artists(e,
                                                  extra=(t=='extraartists'))))

            elif t in ('videos'):
                setattr(release, t, list(self.element_videos(e)))

            elif t in ('labels'):
                setattr(release, t, list(self.element_labels(e)))

            elif t in ('formats'):
                setattr(release, t, list(self.element_formats(e)))

            elif t in ('tracklist'):
                setattr(release, t, list(self.element_tracklist(e)))

            elif t in ('identifiers'):
                setattr(release, t, list(self.element_identifiers(e)))

            elif t in ('companies'):
                setattr(release, t, list(self.element_companies(e)))
        return release
