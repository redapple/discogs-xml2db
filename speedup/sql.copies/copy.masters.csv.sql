-- CREATE TABLE master (
    -- id              integer NOT NULL,
    -- title           text NOT NULL,
    -- year            integer,
    -- main_release    integer NOT NULL,
    -- data_quality    text
-- );

\copy master (id, title, year, main_release, data_quality) FROM '/home/paul/dl/discogs/20170201/discogs.masters.csv' WITH CSV;


-- CREATE TABLE master_artist (
    -- master_id       integer NOT NULL,
    -- artist_id       integer NOT NULL,
    -- anv             text,
    -- join_string     text,
    -- role            text
-- );

\copy master_artist (master_id, artist_id, anv, join_string, role) FROM '/home/paul/dl/discogs/20170201/discogs.masters_artists.csv' WITH CSV;

-- CREATE TABLE master_video (
    -- master_id       integer NOT NULL,
    -- duration        integer,
    -- title           text,
    -- description     text,
    -- uri             text
-- );
\copy master_video (master_id, duration, title, description, uri) FROM '/home/paul/dl/discogs/20170201/discogs.masters_videos.csv' WITH CSV;

-- CREATE TABLE master_genre (
    -- master_id       integer NOT NULL,
    -- genre           text
-- );
\copy master_genre (master_id, genre) FROM '/home/paul/dl/discogs/20170201/discogs.masters_genres.csv' WITH CSV;

-- CREATE TABLE master_style (
    -- master_id       integer NOT NULL,
    -- style           text
-- );
\copy master_style (master_id, style) FROM '/home/paul/dl/discogs/20170201/discogs.masters_styles.csv' WITH CSV;

