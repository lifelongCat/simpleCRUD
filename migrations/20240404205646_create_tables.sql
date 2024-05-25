-- migrate:up
create extension if not exists "uuid-ossp";

create schema if not exists music;

create table music.musician
(
    id uuid primary key default uuid_generate_v4(),
    first_name text,
    last_name text,
    birth_date date
);

create table music.music_piece
(
    id uuid primary key default uuid_generate_v4(),
    title text,
    genre text,
    duration int
);

create table music.musician_to_piece
(
    musician_id uuid references music.musician on delete cascade,
    piece_id uuid references music.music_piece on delete cascade,
    primary key (musician_id, piece_id)
);

create table music.award
(
    id uuid primary key default uuid_generate_v4(),
    musician_id uuid references music.musician on delete cascade,
    title text,
    year int
);

-- migrate:down
drop extension if exists "uuid-ossp";
drop schema if exists music;
