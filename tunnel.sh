#!/bin/bash

case $1 in
start)
  /bin/sh ./tunnel_wiki.sh start
  /bin/sh ./tunnel_people.sh start
  ;;
stop)
  /bin/sh ./tunnel_wiki.sh stop
  /bin/sh ./tunnel_people.sh stop
  ;;
status)
  /bin/sh ./tunnel_wiki.sh status
  /bin/sh ./tunnel_people.sh status
  ;;
*)
  echo "Invalid command $1" >&2
  exit 1
esac

