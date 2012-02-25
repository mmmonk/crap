#!/bin/sh

CHECK=`ssh -O check $1 2>&1 | grep "Connection refused"`
if [ "x$CHECK" != "x" ]; then
  SOCKET=`echo $CHECK | perl -npe 's/^.+\((.+?)\).*/$1/'`
  rm $SOCKET
fi 

CT=`date +%s`
LT=$CT
DEFAULTSLEEP=5
SLEEP=$DEFAULTSLEEP
C=0

while [ 1 = 1 ]
do
	eval "ssh $*"


  ### backoff mechanism 
  CT=`date +%s`
  DIFF=`expr $CT - $LT`
  LT=$CT
  if [ $DIFF -ge 1800 ]; then
    SLEEP=$DEFAULTSLEEP
  fi

  if [ $SLEEP -le 300 ]; then
    if [ $C -ge 3 ]; then
      SLEEP=`expr $SLEEP \* 2`  
      C=0
    fi
    C=`expr $C + 1`
  fi
 
  TS=`date "+%Y/%m/%d %H:%M:%S"`
  echo "--- $TS - $SLEEP:$C : press ctrl+c to exit ---"
  sleep $SLEEP 
done
