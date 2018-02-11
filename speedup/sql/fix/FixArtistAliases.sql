--- artist_alias
--- Discogs dump only contain the alias name
--- the corresponding artist ID must be resolved
UPDATE artist_alias AS aa
SET alias_artist_id = a.id
FROM artist AS a
WHERE aa.alias_name = a.name
