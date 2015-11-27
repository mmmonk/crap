#!/bin/sh

git sync;
git branch | tr -d \* | xargs -t -n 1 git up1
