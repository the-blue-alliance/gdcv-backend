#! /bin/bash

service mysql start
mysql -sfu root < "./scripts/mysql_install.sql"
