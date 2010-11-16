#!/bin/sh

tmux has-session -t $1

if [ $? = 0 ]; then
  tmux attach -t $1 
else
  if [ $1 = $0 ]; then
    tmux new-session -n 0 \; \
      rename-window -t 0 ekg \; \
      new-window -d -n tao -t 1 \; \
      split-window -d -h -t 1 'mutt' \; \
      new-window -d -n rudy -t 2 'ssh_keep.sh r' \; \
      new-window -d -n xls -t 3 'ssh_keep.sh x' \; \
      new-window -d -n logs -t 4 'sudo tail --follow=name /var/log/messages' \; \
      split-window -d -h -t 4 'sudo tail --follow=name /var/log/auth.log | grep -v CRON' \; \
      new-window -d -t 5
  else
    tmux new-session -n $1
  fi
fi
