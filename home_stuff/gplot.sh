#!/bin/sh

TITLE="notitle"

if [ "x$1" != "x" ]; then
  TITLE="title \"$1\""
fi

gnuplot -p -e "set autoscale;plot \"< cat /proc/\$\$/fd/0\" $TITLE with lines"
