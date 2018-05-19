#!/bin/sh

if [ "a" != "a$1" ]; then
  OK="0"
  for host in $(egrep '^host' ~/.ssh/config | grep -v '\*' | pcregrep -o "\s+$1\S*?(\s|$)")
  do
    OK="1"
    STYLE=$(pcregrep -A1 "\s$host(\s|$)" ~/.ssh/config | grep -o 'tmux-style: .*' | cut -d' ' -f2-)
    tmux send-keys "ssh $host" \; select-pane -P "$STYLE" \; split-window \; select-layout tiled
  done
  if [ $OK = "1" ]; then
    tmux set-window-option synchronize-panes \; send-keys ENTER
    tmux kill-pane \; select-layout tiled
  fi
fi
