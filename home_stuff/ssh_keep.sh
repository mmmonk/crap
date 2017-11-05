#!/bin/sh

CHECK=`ssh -O check $1 2>&1 | grep "Connection refused"`
if [ "x$CHECK" != "x" ]; then
  SOCKET=`echo $CHECK | perl -npe 's/^.+\((.+?)\).*/$1/'`
  rm $SOCKET
fi 

CT=`date +%s`
LT=$CT
DEFAULTSLEEP=2
MAXSLEEP=$DEFAULTSLEEP
C=0

while [ 1 = 1 ]
do
  eval "ssh $*"

  ### backoff mechanism 
  CT=`date +%s`
  DIFF=`expr $CT - $LT`
  LT=$CT
  if [ $DIFF -ge 1800 ]; then
    MAXSLEEP=$DEFAULTSLEEP
    C=0
  fi

  if [ $MAXSLEEP -le 180 ]; then
    if [ $C -ge 5 ]; then
      MAXSLEEP=`expr $MAXSLEEP \* 2`
      C=0
    fi
    C=`expr $C + 1`
  fi

  TS=`date "+%Y/%m/%d %H:%M:%S"`

  # this make the reconnect a bit more random
  # the HALF part makes sure we will always
  # get the value from the higher part of the MAXSLEEP
  HALF=`expr $MAXSLEEP / 2`
  SLEEP=`expr $CT % $HALF + $HALF + 1`
  echo "--- $TS - $SLEEP:$MAXSLEEP:$C : press ctrl+c to exit ---"
  sleep $SLEEP
done
