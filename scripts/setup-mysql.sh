#! /bin/bash

service mysql stop
mysqld_safe --skip-grant-tables --skip-networking &
sleep 2
echo "Resetting mysql permissions"
mysql -u root < "./scripts/mysql_install.sql"
service mysql stop
