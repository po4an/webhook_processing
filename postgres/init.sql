-- create schema
create schema if not exists service;

-- create table
create table if not exists service.log  (
    id serial,
    data text,
    func varchar(64),
    load_dttm timestamp without time zone default clock_timestamp()
);