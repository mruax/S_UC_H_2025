cd moodle-docker
export MOODLE_DOCKER_WWWROOT=./moodle
export MOODLE_DOCKER_DB=pgsql
cp config.docker-template.php $MOODLE_DOCKER_WWWROOT/config.php
bin/moodle-docker-compose up -d --build
bin/moodle-docker-wait-for-db
cd ..
docker compose up -d --build
