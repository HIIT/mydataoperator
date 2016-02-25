#!/bin/sh
/etc/init.d/apache2 start
/etc/init.d/mysql start
cd /~
sh run_all.sh
