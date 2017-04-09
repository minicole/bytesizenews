#!/bin/bash

# Stop and start all supervisor services
supervisorctl stop ByteSizeNews
supervisorctl stop bytesizenewscelerybeat
supervisorctl stop bytesizenewscelery

supervisorctl start ByteSizeNews
supervisorctl start bytesizenewscelerybeat
supervisorctl start bytesizenewscelery
