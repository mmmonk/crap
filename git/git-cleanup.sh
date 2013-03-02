#!/bin/sh

git remote prune origin
git gc --auto
#git gc --aggressive
git repack -a -d --depth=250 --window=250

