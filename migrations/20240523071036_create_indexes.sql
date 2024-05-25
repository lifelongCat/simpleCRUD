-- migrate:up
create extension if not exists pg_trgm;
create index if not exists musician_birth_date_idx on music.musician using btree(birth_date);
create index if not exists musician_name_and_lastname_idx
    on music.musician using gist(first_name gist_trgm_ops, last_name gist_trgm_ops);

-- migrate:down
drop extension if exists pg_trgm;
drop index if exists idk_index, idk2_index;
