#!/bin/zsh

docker run -dit -p 25580:80 --name mc-map -v $PWD/server-map:/usr/share/caddy caddy
