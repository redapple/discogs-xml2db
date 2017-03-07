\copy artist (id, name, realname, profile, data_quality) FROM PROGRAM 'bzcat ./artist.csv.bz2' WITH CSV;
\copy artist_alias (artist_id, alias_name) FROM PROGRAM 'bzcat ./artist_alias.csv.bz2' WITH CSV;
\copy artist_namevariation (artist_id, name) FROM PROGRAM 'bzcat ./artist_namevariation.csv.bz2' WITH CSV;
\copy artist_url (artist_id, url) FROM PROGRAM 'bzcat ./artist_url.csv.bz2' WITH CSV;
\copy group_member (group_artist_id, member_artist_id, member_name) FROM PROGRAM 'bzcat ./group_member.csv.bz2' WITH CSV;

