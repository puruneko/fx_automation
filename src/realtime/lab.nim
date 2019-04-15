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
import "./indicator"
import "./utils"
import "./extraMath"
import "./PhaseTimer"


proc correlation(longer: Indicator, shorter: Indicator): float =
  let longer2 = longer[longer.len-shorter.len..<longer.len]
  let shorter2 = adjustPower(shorter, longer)
  let longerAvg = longer2.meanStatic()
  let shorterAvg = shorter2.meanStatic()
  let longerSgm2 = longer2.sgm2
  let shorterSgm2 = shorter2.sgm2()
  let mother = sqrt(longerSgm2*shorterSgm2)
  for i in 0..<shorter.len:
    result += (longer2[i]-longerAvg)*(shorter2[i]-shorterAvg)/mother

type
  TestType = object
    val: Table[string, seq[float]]
    meta: seq[float]

proc `[]`(t: TestType, label: string, slice: HSlice): seq[float] =
  return t.val[label][slice]

#[
proc main(pt: var PhaseTimer) =
  # 準備
  const ohlc_flag = true
  const N = 64
  let ohlc = getHistricalData(r"./../../resources/DAT_ASCII_EURUSD_M1_2007.csv", ';', 0, N)
  var close = ohlc[4].removeBias()
  #close = close[0..6].concat(close[0..6]).concat(close[0..6]).concat(close[0..6])
  # DWT(単位を全部任意単位に合わせるため、時間tと係数a,bの単位を消す -> 番号で表現) # 本当は t,a,b
  pt.phase("test"):
    #let close = @[3.0, -3.0, 1.0, -1.0, 1.0, -1.0, -2.0, -4.0, -5.0, -2.0, 1.0, 4.0, 5.0, 12.0, 7.0]
    #let close = @[3.0, -3.0, 1.0, -1.0, 1.0, -1.0, -2.0, -4.0, -5.0, -2.0, 1.0, -1.0, 1.0, -1.0, 1.0]
    echo("----- close -----\n", close)
    let rangeWavelet = lc[close.meanStatic() | (x <- 0..10), float] #close.limitedSequence(1.0)
    echo("----- range wavelet -----\n", rangeWavelet)
    let coef = (max(close[close.len-rangeWavelet.len..<close.len])-min(close[close.len-rangeWavelet.len..<close.len]))/float(rangeWavelet.len)
    let trendWavelet = lc[min(close[close.len-rangeWavelet.len..<close.len]) + float(x) * coef | (x <- 0..<rangeWavelet.len), float]
    echo("----- trend wavelet -----\n", trendWavelet)
    echo("---------------")
    echo("range:  ", correlation(close, rangeWavelet))
    echo("trend:  ", correlation(close, trendWavelet))
]#

proc main(pt: PhaseTimer) =
  var t: TestType = TestType(val: {"test": @[1.0, 2.0, 3.0, 4.0]}.toTable())
  echo(t["test", 0..1])

  
if isMainModule:
  var pt = initPhaseTimer()
  pt.phase("LAB"):
    main(pt)