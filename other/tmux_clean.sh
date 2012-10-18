#!/bin/sh

for paneid in `tmux list-panes -s | awk -F":" '{print $1}'`
do
  tmux clear-history -t $paneid
done

for buffid in `tmux list-buffers | awk -F":" '{print $1}'`
do
  tmux delete-buffer -b $buffid
done

