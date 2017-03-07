\copy label ( id, name, contact_info, profile, parent_name, data_quality ) FROM PROGRAM 'bzcat label.csv.bz2' WITH CSV;
\copy label_url ( label_id, url ) FROM PROGRAM 'bzcat label_url.csv.bz2' WITH CSV;

