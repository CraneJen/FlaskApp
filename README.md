# FlaskApp
A simple project built with flask


### DATABASE Postgresql  
TABLE users  
```
CREATE TABLE users (
    id serial,
    name varchar(100),
    username varchar(100),
    email varchar(150) not null,
    password varchar(100) not null,
    PRIMARY KEY(id, username)
    )
```
