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

import "./simulation"

proc getHistricalData*(path: string, sep=';'): Candle {.inline.} =
  var fp: File
  defer: fp.close()
  var openOk = fp.open(path, fmRead)
  if openOk:
    var i = 0
    for line in fp.lines():
      if loadHistorical_start <= i and i < loadHistorical_end:
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
