#!/bin/sh

GUISVR_DIR="/usr/netscreen/GuiSvr/"
GUISVR_UTILS_DIR="$GUISVR_DIR/utils"

DBXML_DIR=`ls -1 -t $GUISVR_UTILS_DIR|grep dbxml| head -n 1`
LD_LIBRARY_PATH=$GUISVR_UTILS_DIR/$DBXML_DIR/lib:$LD_LIBRARY_PATH

export LD_LIBRARY_PATH
#echo LD_LIBRARY_PATH=$LD_LIBRARY_PATH
#echo $GUISVR_UTILS_DIR/$DBXML_DIR/bin/

if [ -f $1 ]; then
  $GUISVR_UTILS_DIR/$DBXML_DIR/bin/dbxml -h $GUISVR_DIR/var/xdb/data/ -s $1
fi
