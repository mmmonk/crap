#!/usr/bin/env python

a="{{[{{{{}}{{}}}[]}[][{}][({[(({{[][()()]}}{[{{{}}}]}))][()]{[[{((()))({}(())[][])}][]()]}{()[()]}]})][]]}{{}[]}}"
b=list()
i=0

for x in a:
  if x == "{" or x=="[":
    b.append(x)
  if x == "}":
    if b[-1] == "{":
      b.pop()
    else:
      print i
  if x == "]":
    if b[-1] == "[":
      b.pop()
    else:
      print i
  i+=1
