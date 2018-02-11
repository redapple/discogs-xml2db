--- label
--- parent/sublabel relationship needs to be resolved by name

UPDATE label
SET parent_id = parent.id
FROM label AS parent
WHERE label.parent_name = parent.name;
