--- artists
ALTER TABLE artist DROP CONSTRAINT IF EXISTS artist_pkey;

--- labels
ALTER TABLE label DROP CONSTRAINT IF EXISTS label_pkey;

--- masters
ALTER TABLE master DROP CONSTRAINT IF EXISTS master_pkey;

--- releases
ALTER TABLE release DROP CONSTRAINT IF EXISTS release_pkey;
ALTER TABLE release_track DROP CONSTRAINT IF EXISTS release_track_pkey;
