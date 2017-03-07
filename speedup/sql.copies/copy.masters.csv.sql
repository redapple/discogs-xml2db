\copy master (id, title, year, main_release, data_quality) FROM PROGRAM 'bzcat ./master.csv.bz2' WITH CSV;
\copy master_artist (master_id, artist_id, anv, join_string, role) FROM PROGRAM 'bzcat ./master_artist.csv.bz2' WITH CSV;
\copy master_video (master_id, duration, title, description, uri) FROM PROGRAM 'bzcat ./master_video.csv.bz2' WITH CSV;
\copy master_genre (master_id, genre) FROM PROGRAM 'bzcat ./master_genre.csv.bz2' WITH CSV;
\copy master_style (master_id, style) FROM PROGRAM 'bzcat ./master_style.csv.bz2' WITH CSV;

