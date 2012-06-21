#!/usr/bin/python

from sys import exit
from os import getenv
from subprocess import check_output

def sendcmd(cmd):
  try:
    open(str(getenv('HOME'))+"/.gg/cmd","w").write(cmd)
  except:
    exit(1)

def state(st):
  cst = "" 
  try:
    cst = open(str(getenv('HOME'))+"/.gg/tmux_state").readline()
  except:
    pass
  if cst == st:
    return 1 
  try:
    open(str(getenv('HOME'))+"/.gg/tmux_state","w").write(st)
  except:
    pass
  return 0 

if __name__ == '__main__':

  out = check_output(["tmux", "list-clients"])

  if "dev" in out:
    if state("connect") == 0:
      sendcmd("/connect\n")
  else:
    if state("disconnected") == 0:
      sendcmd("/disconnect\n")
