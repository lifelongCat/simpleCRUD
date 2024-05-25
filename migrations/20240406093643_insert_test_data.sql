-- migrate:up
insert into music.musician (first_name, last_name, birth_date)
values ('Edward', 'Sheeran', '1958-08-29'),
       ('Michael', 'Noskov', '2006-02-14'),
       ('Hello', 'World', '1970-01-01'),
       ('Post', 'Malone', '1995-07-04');

insert into music.music_piece (title, genre, duration)
values ('Perfect', 'Soft-rock', 263),
       ('Bad Habits', 'Dance-pop', 231),
       ('My song', 'Cringe', 142),
       ('Sunflower', 'Dream-pop', 159);

insert into music.musician_to_piece (musician_id, piece_id)
values ((select id from music.musician where first_name = 'Edward' and last_name = 'Sheeran'),
        (select id from music.music_piece where title = 'Perfect')),
       ((select id from music.musician where first_name = 'Edward' and last_name = 'Sheeran'),
        (select id from music.music_piece where title = 'Bad Habits')),
       ((select id from music.musician where first_name = 'Michael' and last_name = 'Noskov'),
        (select id from music.music_piece where title = 'My song')),
       ((select id from music.musician where first_name = 'Post' and last_name = 'Malone'),
        (select id from music.music_piece where title = 'Sunflower'));

insert into music.award (musician_id, title, year)
values ((select id from music.musician where first_name = 'Edward' and last_name = 'Sheeran'),
        'World Music', 2014),
       ((select id from music.musician where first_name = 'Post' and last_name = 'Malone'),
        'Pollstar Awards', 2020),
       ((select id from music.musician where first_name = 'Post' and last_name = 'Malone'),
        'Juno Awards', 2019),
       ((select id from music.musician where first_name = 'Post' and last_name = 'Malone'),
        'American Music Awards', 2018);

-- random data generator
insert into music.musician (first_name, last_name, birth_date)
select md5(random()::text), md5(random()::text),
       random() * (timestamp '2024-05-24 00:00:00' - timestamp '2023-05-24 00:00:00') + timestamp '2023-05-24 00:00:00'
from generate_series(1, 100000);

-- migrate:down
truncate music.musician, music.music_piece, music.musician_to_piece, music.award;
