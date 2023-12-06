#!/bin/env bash

# creates a database
CREATE DATABASE $db_name;

# create user
CREATE USER "$user_name"@"localhost" IDENTIFIED BY "$user_pwd";

# grant privildges to app
GRANT ALL PRIVILEGES ON "$db_name".* TO "$user_name"@"localhost";

FLUSH PRIVILEGES
