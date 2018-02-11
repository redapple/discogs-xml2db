--- release label
--- label id is empty, there's only the label's name

UPDATE release_label
SET label_id = label.id
FROM label
WHERE label.name = release_label.label_name;
