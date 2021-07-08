#!/bin/bash
set -e

PIDFILE=tunnel_people.pid

TUN=0.0.0.0:33069:cadidb.epfl.ch:3306
SSHCMD="ssh -T -N -L $TUN dinfo@dinfo1.epfl.ch"

start() {
  if [ "$(status)" != "running" ] ; then
    $SSHCMD &
    NPID=$!
    if [ "$(status)" == "running" ] ; then
      echo "Started DB tunnel with PID=$NPID"
      echo "$NPID" > $PIDFILE
    else
      echo "Could not start DB tunnel" >&2
      exit 1
    fi
  fi
}

stop() {
  if [ "$(status)" == "running" ] ; then
    OPID=$(cat $PIDFILE)
    echo "Trying to kill tunnel process with pid '$OPID'"
    if kill $OPID ; then
      rm -f $PIDFILE 
    else
      echo "Could not kill DB tunnel running with pid $OPID"
    fi
  fi
}

# return tunnel status and perform housekeeping
status() {
  if ps ax | grep "$SSHCMD" | grep -q -v grep ; then
    ret="running"
    TPID=$(ps ax | awk "/awk/{next;}/$SSHCMD/{print \$1;}")
    if [ -f $PIDFILE ] ; then
      OPID=$(cat $PIDFILE)
      if [ "$OPID" != "$TPID" ] ; then
        echo "DB tunnel pid file is present but wrong: true/saved pid=$TPID/$OPID. Fixing." >&2
        echo "$TPID" > $PIDFILE
      fi
    else
      echo "DB tunnel pid file not present. Creating it." >&2
      echo "$TPID" > $PIDFILE
    fi
  else
    ret="stopped"
    [ -f $PIDFILE ] && rm -f $PIDFILE
  fi
  echo "$ret"
}

case $1 in
start)
  start
  ;;
stop)
  stop
  ;;
status)
  echo "Tunnel for people is $(status)"
  ;;
*)
  echo "Invalid command $1" >&2
  exit 1
esac

