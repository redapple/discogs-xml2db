--- release track
-- CREATE TABLE release_track (
    -- id              SERIAL,
    -- release_id      integer NOT NULL,
    -- sequence        integer NOT NULL,
    -- position        text,
    -- parent          integer,
    -- title           text,
    -- duration        text
-- );
-- CREATE TABLE release_track_artist (
    -- id              SERIAL,
    -- track_id        integer,
    -- release_id      integer NOT NULL,
    -- track_sequence  integer NOT NULL,
    -- artist_id       integer NOT NULL,
    -- artist_name     text,
    -- extra           boolean NOT NULL,
    -- anv             text,
    -- join_string     text,
    -- role            text,
    -- tracks          text
-- );

-- SELECT
    -- release_track_artist.id,
    -- release_track_artist.release_id,
    -- release_track_artist.track_sequence,
    -- release_track_artist.position,
    -- release_track_artist.artist_id,
    -- release_track.id AS track_id
-- FROM release_track_artist
-- JOIN release_track
-- ON release_track.release_id = release_track_artist.release_id
-- AND release_track.sequence = release_track_artist.track_sequence
--WHERE label.id IS NULL;


UPDATE release_track_artist
SET track_id = release_track.id
FROM release_track
WHERE release_track.release_id = release_track_artist.release_id
AND release_track.sequence = release_track_artist.track_sequence;
