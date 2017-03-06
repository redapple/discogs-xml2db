\copy artist (id, name, realname, profile, data_quality) FROM '/home/paul/dl/discogs/20170201/discogs.artists.csv' WITH CSV;
\copy artist_alias (artist_id, alias_name) FROM '/home/paul/dl/discogs/20170201/discogs.artists_aliases.csv' WITH CSV;
\copy artist_namevariation (artist_id, name) FROM '/home/paul/dl/discogs/20170201/discogs.artists_variations.csv' WITH CSV;
\copy artist_url (artist_id, url) FROM '/home/paul/dl/discogs/20170201/discogs.artists_urls.csv' WITH CSV;
\copy group_member (group_artist_id, member_artist_id, member_name) FROM '/home/paul/dl/discogs/20170201/discogs.groups_members.csv' WITH CSV;

