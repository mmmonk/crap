#!/bin/sh

wid=0

for cwid in `tmux list-windows | awk -F":" '{print $1}'`
do
  if [ $cwid != $wid ]; then
    tmux move-window -d -s $cwid -t $wid
  fi
  wid=`expr $wid + 1`
done
