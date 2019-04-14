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

import "./core"

proc nowString*(): string =
  return format(now(), "YYYY/MM/dd HH:mm:ss")

proc displayError*(msg: string) =
  echo("*".repeat(msg.len))
  echo(msg)
  echo("*".repeat(msg.len))

proc getHistricalData*(path: string, sep=';', startPoint: int = 0, endPoint: int = -1): Candle {.inline.} =
  var fp: File
  defer: fp.close()
  var openOk = fp.open(path, fmRead)
  if openOk:
    var endPointUpdate = endPoint
    if endPointUpdate == -1:
      endPointUpdate = high(int)
    var i = 0
    for line in fp.lines():
      if startPoint <= i and i < endPointUpdate:
        let splitted = line.split(sep)
        if splitted.len != 6:
          continue
        result.time.add(parse(splitted[0], "yyyyMMdd hhmmss", utc()))
        result.open.add(parseFloat(splitted[1]))
        result.high.add(parseFloat(splitted[2]))
        result.low.add(parseFloat(splitted[3]))
        result.close.add(parseFloat(splitted[4]))
        result.volume.add(parseFloat(splitted[5]))
      inc(i)
  else:
    displayError(fmt"{path} open error.")

proc recordProcTime*(basePath: string, procTime: float) =
  let path = joinPath(basePath, "procTimeHistory.csv")
  var fp: File
  defer: fp.close()
  var openOk = fp.open(path, fmAppend)
  if openOk:
    let ns = nowString()
    let newLine = "\n"
    fp.write(fmt"{ns},{procTime}{newLine}")

proc direction*(a: float, b: float): int =
  if float(a) != float(b): int((b-a)/abs(b-a)) else: 0

proc sign*(x: float): float =
  x/abs(x)

proc sign*(x: int): int =
  int(float(x)/float(abs(x)))
   
proc uSqrt*(x: float): float =
  return sign(x) * sqrt(abs(x))

proc uLog10*(x: float): float =
  return sign(x) * log10(abs(x))

proc absMax*(x: openArray[float]): float =
  result = -Inf
  for y in x:
    if result < abs(y):
      result = y

proc absMin*(x: openArray[float]): float =
  result = +Inf
  for y in x:
    if result > abs(y):
      result = y

proc adjustFigure*(x: float, figure: float = 0.0): float =
  if x == 0.0:
    return 0.0
  return x * pow(10.0, -log10(x).floor) * pow(10.0, figure)