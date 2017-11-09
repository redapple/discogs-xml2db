--- artists
ALTER TABLE artist ADD CONSTRAINT artist_pkey PRIMARY KEY (id);

--- labels
ALTER TABLE label ADD CONSTRAINT label_pkey PRIMARY KEY (id);

--- masters
ALTER TABLE master ADD CONSTRAINT master_pkey PRIMARY KEY (id);

--- releases
ALTER TABLE release ADD CONSTRAINT release_pkey PRIMARY KEY (id);
ALTER TABLE release_track ADD CONSTRAINT release_track_pkey PRIMARY KEY (release_id, sequence);
ALTER TABLE release_track_artist ADD CONSTRAINT release_track_artist_pkey PRIMARY KEY (id);
