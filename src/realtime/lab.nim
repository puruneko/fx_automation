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
import typetraits
import queues

import "./core"
import "./indicator"
import "./utils"
import "./extraMath"
import "./PhaseTimer"

type
  TestType = object
    val: Table[string, seq[float]]
    meta: seq[float]

proc `[]`(t: TestType, label: string, slice: HSlice): seq[float] =
  return t.val[label][slice]

proc main(pt: var PhaseTimer) =
  # 準備
  const ohlc_flag = true
  const N = 1024
  let ohlc = getHistricalData(r"./../../resources/DAT_ASCII_EURUSD_M1_2007.csv", ';', 0, N)
  var close = ohlc[4].removeBias()
  #close = close[0..6].concat(close[0..6]).concat(close[0..6]).concat(close[0..6])
  pt.phase("test"):
    #let close = @[3.0, -3.0, 1.0, -1.0, 1.0, -1.0, -2.0, -4.0, -5.0, -2.0, 1.0, 4.0, 5.0, 12.0, 7.0]
    #let close = @[3.0, -3.0, 1.0, -1.0, 1.0, -1.0, -2.0, -4.0, -5.0, -2.0, 1.0, -1.0, 1.0, -1.0, 1.0]
    echo("close")
    echo(close)
    let spectrum = close.dct()
    echo("spectrum")
    echo(spectrum)
  pt.phase("popTest"):
    var a: Queue = initQueue[int]()
    a.add(1)
    a.add(2)
    a.pop()
    echo(a)

#[

proc main(pt: PhaseTimer) =
  var t: TestType = TestType(val: {"test": @[1.0, 2.0, 3.0, 4.0]}.toTable())
  echo(t["test", 0..1])
  echo(($type(main)).startsWith("proc"))
]#

  
if isMainModule:
  var pt = initPhaseTimer()
  pt.phase("LAB"):
    main(pt)