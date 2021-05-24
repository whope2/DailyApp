#!/bin/sh
nginx
uwsgi --ini dailyapp.ini
