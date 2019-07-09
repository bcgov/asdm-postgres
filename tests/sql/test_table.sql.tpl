
create table working_data.${TABLE} (
    name varchar(20),
    primary key (name)
);

insert into working_data.${TABLE} values ('Joe');
insert into working_data.${TABLE} values ('Marie');
