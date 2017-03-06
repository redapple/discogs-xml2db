\copy label ( id, name, contact_info, profile, parent_name, data_quality ) FROM '/home/paul/dl/discogs/20170201/discogs.labels.csv' WITH CSV;
\copy label_url ( label_id, url ) FROM '/home/paul/dl/discogs/20170201/discogs.labels_urls.csv' WITH CSV;

