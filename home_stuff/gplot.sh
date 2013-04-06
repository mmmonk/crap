#!/bin/sh

TITLE="notitle"
XLABEL=" "
YLABEL=" "
STYLE="lines"

if [ "x$1" != "x" ]; then
  STYLE=$1
fi

if [ "x$2" != "x" ]; then
  TITLE="title \"$2\""
fi

if [ "x$3" != "x" ]; then
  XLABEL=$3
fi

if [ "x$4" != "x" ]; then
  YLABEL=$4
fi

#  set object 1 rect from screen 0, 0 to screen 1, 1 behind fc rgb \"white\" fillstyle solid 1.0;\
#  set object 2 rect from screen 0.14, 0.12 to screen 0.97, 0.96 behind fc rgb \"white\" fillstyle solid 1.0;\

gnuplot -p -e "set autoscale;\
  set xlabel \"$XLABEL\" tc rgb \"black\";\
  set ylabel \"$YLABEL\" tc rgb \"black\";\
  set grid xtics lt 0 lw 1 lc rgb \"#AAAAAA\";\
  set grid ytics lt 0 lw 1 lc rgb \"#AAAAAA\";\
  set border lc rgb \"black\";\
  plot \"-\" $TITLE with $STYLE lc rgb \"red\";"
