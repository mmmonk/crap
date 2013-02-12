#!/bin/sh

socat - SOCKS:127.0.0.1:$1:$2,cork=1
