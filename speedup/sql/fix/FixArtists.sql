--- artist
--- the combination `\"` makes neo4j's import tool choke
UPDATE artist SET profile=translate(profile, E'\\"', '″') WHERE name LIKE E'%\\"%';
