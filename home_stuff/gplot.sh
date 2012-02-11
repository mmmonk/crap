#!/bin/sh

ARGS="notitle with lines lc rgbcolor \"red\""

if [ "x$1" != "x" ]; then
  ARGS=$1
fi

gnuplot -p -e "plot \"< cat /proc/\$\$/fd/0\" $ARGS"  
