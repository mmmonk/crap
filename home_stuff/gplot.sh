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

gnuplot -p -e "set autoscale;\
  set xlabel \"$XLABEL\" tc rgb \"white\";\
  set ylabel \"$YLABEL\" tc rgb \"white\";\
  set grid xtics lt 0 lw 1 lc rgb \"#AAAAAA\";\
  set grid ytics lt 0 lw 1 lc rgb \"#AAAAAA\";\
  set object 1 rect from screen 0, 0 to screen 1, 1 behind fc rgb \"black\" fillstyle solid 1.0;\
  set object 2 rect from screen 0.14, 0.12 to screen 0.97, 0.96 behind fc rgb \"#555555\" fillstyle solid 1.0;\
  set border lc rgb \"white\";\
  plot \"< cat /proc/\$\$/fd/0\" $TITLE with $STYLE lc rgb \"red\";"
