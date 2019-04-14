import sugar
import os
import system
import nre
import times
import math
import tables
import strutils
import sequtils
import strformat

type Bracket = seq[(string,float)]

proc `&&`[T,U](pair: openArray[(T,U)]): Table[T,U] =
  pair.toTable

proc sample(t: Table) =
  echo("proc sample")
  for key, elem in t:
    echo(elem)

proc lcTest(n: int): float =
  let start_time = cpuTime()
  var x: seq[float] = @[]
  x = lc[float(x)*0.5 | (x <- countup(0,n)), float]
  return cpuTime()-start_time

proc forTest(n: int): float =
  var start_time = cpuTime()
  var y: seq[float] = @[]
  for i in countup(0,n):
    y.add(float(i)*0.5)
  return cpuTime()-start_time

proc main() =
  sample(&&{"a":1.0, "b":2.0})
  sample(initTable[string, float]())
  #[
  let n = 10000000
  var res: array[2, seq[float]]
  res[0] = @[]
  res[1] = @[]
  for i in countup(0,100):
    if i mod 2 == 0:
      res[0].add(lcTest(n))
      res[1].add(forTest(n))
    else:
      res[1].add(forTest(n))
      res[0].add(lcTest(n))
  echo(fmt"lc  average:{sum(res[0])/float(res[0].len)}")
  echo(fmt"for average:{sum(res[1])/float(res[1].len)}")
  ]#
  for i in countup(0,10):
    echo(i)
if isMainModule:
  main()