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
import algorithm

import "./core"
import "./utils"
import "./extraMath"
import "./phaseTimer"

type
  Rolling* = seq[float]
  Edge = tuple[direction: DirectionType, itr: int]
  Edges = seq[Edge]


template argAdjustment[T](arg: T, errorValue:T, defaultValue: T): T =
  if arg == errorValue: defaultValue else: arg

proc rolling*(ind: Indicator, itr: int, period: int): Rolling =
  return ind[itr-period+1..itr]

proc divide*(rolling: Rolling): float =
  return (rolling[rolling.len-1]-rolling[0])/float(rolling.len)

proc ma*(ind: Indicator): float =
  return ind.mean()

proc ma*(ind: Indicator, itr: int, period: int): float =
  if itr < period:
    return NaN
  return ind.rolling(itr, period).mean()

proc maDouble*(ind: Indicator, itr: int, period: int): float =
  if itr < period:
    return NaN
  let rolling = ind.rolling(itr, period)
  let avg = rolling.mean()
  return sqrt(lc[avg + x*x*sign(x) | (x <- rolling), float].mean())

proc diff*(ind: Indicator, itr: int, period: int): float =
  if itr < period:
    return NaN
  return ind.rolling(itr, period).divide()

proc count*(ind: Indicator, itr: int, period: int, condition: proc(x: float): bool = (proc(x:float): bool = true)): int =
  if itr < period:
    return 0
  for x in ind[itr-period+1..itr]:
    if condition(x):
      inc(result)

proc limitedSequence*(sequence: seq[float], sgmCoef: float = 1.0): seq[float] =
  let s = sequence.removeBias()
  let allSgm = s.sgm()
  return lc[x | (x <- s, -allSgm*sgmCoef < x and x < allSgm*sgmCoef), float]

proc limitedOverSequence*(sequence: seq[float], sgmCoef: float = 1.0): seq[float] =
  let s = sequence.removeBias()
  let allSgm = s.sgm()
  return lc[x | (x <- s, -allSgm*sgmCoef >= x or x >= allSgm*sgmCoef), float]

proc dropNan*(ind: Indicator): Indicator =
  lc[x | (x <- ind, x != NaN), float]

proc detectEdge*(upper: Indicator, lower: Indicator, itr:int, edgeUnitHeight: float, edgeUnitHalfWidth: int, judgeType="full"): float =
  if itr < edgeUnitHalfWidth*2 + 1:
    return NaN
  let center = itr - edgeUnitHalfWidth
  # 上側頂点の検出
  if upper[itr] >= max(upper[center-edgeUnitHalfWidth..itr]):
    let rightMinSum = min(lower[center-edgeUnitHalfWidth..<center])
    let leftMinSum  = min(lower[center+1..itr])
    if judgeType == "full":
      if rightMinSum > edgeUnitHeight and leftMinSum > edgeUnitHeight:
        return upper[itr]
    else:
      if rightMinSum > edgeUnitHeight or leftMinSum > edgeUnitHeight:
        return upper[itr]
  # 下側頂点の検出
  if lower[itr] >= min(lower[center-edgeUnitHalfWidth..itr]):
    let rightMaxSum = max(upper[center-edgeUnitHalfWidth..<center])
    let leftMaxSum  = max(upper[center+1..itr])
    if judgeType == "full":
      if rightMaxSum > edgeUnitHeight and leftMaxSum > edgeUnitHeight:
        return lower[itr]
    else:
      if rightMaxSum > edgeUnitHeight or leftMaxSum > edgeUnitHeight:
        return lower[itr]
  return NaN



proc main(pt: var PhaseTimer) =
  # 準備
  const ohlc_flag = true
  const N = 16
  const P = 4
  const period = 1
  var signal: seq[float]
  var a: seq[float]
  if ohlc_flag:
    let ohlc = getHistricalData(r"./../../resources/DAT_ASCII_EURUSD_M1_2007.csv", ';', 0, N)
    if P != 0:
      signal = raisedCosineInterpolation2(ohlc.close, P)
    else:
      if period <= 1:
        signal = lc[x-mean(ohlc.close) | (x <- ohlc.close), float]
      else:
        for i in 0..<ohlc.close.len:
          if i < period-1:
            signal.add(ohlc.close[0])
          else:
            signal.add(sum(ohlc.close[i-(period-1)..i])/float(period))
  else:
    let t = lc[-1.0+float(i)/(float(N)*0.5) | (i <- 0..<N), float]
    let sig_org = lc[cos(2.0 * PI * 7.0 * tt) + sin(PI * 6.0 * tt) | (tt <- t), float]
    if P != 0:
      signal = raisedCosineInterpolation2(sig_org, P)
    else:
      signal = sig_org
  # DWT(単位を全部任意単位に合わせるため、時間tと係数a,bの単位を消す -> 番号で表現) # 本当は t,a,b
  pt.enter("DCT")
  let w = dct(signal)
  pt.leave("DCT")
  # IDWT
  pt.enter("IDCT")
  let signal_inv = idct(w)
  if NaN in signal_inv:
    echo("!!!! NAN detected !!!!")
  pt.leave("IDCT")
  pt.enter("process")
  let w2 = wFilter(w, 16)
  let signal_inv2 = idct(w2)
  pt.leave("process")
  

  ######
  pt.enter("output")
  var path: string
  var fp: File
  var openOk: bool
  path = joinPath(".", "dct.csv")
  openOk = fp.open(path, fmWrite)
  if openOk:
    defer: fp.close()
    for elem in w:
      fp.write(fmt"{elem}{'\n'}")
  else:
    echo(fmt"{path} open failed")
  path = joinPath(".", "dct2.csv")
  openOk = fp.open(path, fmWrite)
  if openOk:
    defer: fp.close()
    for elem in w2:
      fp.write(fmt"{elem}{'\n'}")
  else:
    echo(fmt"{path} open failed")
  path = joinPath(".", "signal_nim.csv")
  openOk = fp.open(path, fmWrite)
  if openOk:
    defer: fp.close()
    for elem in signal:
        fp.write(fmt"{elem}")
        fp.write("\n")
  else:
    echo(fmt"{path} open failed")
  path = joinPath(".", "signal_nim_inverse.csv")
  openOk = fp.open(path, fmWrite)
  if openOk:
    defer: fp.close()
    for elem in signal_inv:
      fp.write(fmt"{elem}")
      fp.write("\n")
  else:
    echo(fmt"{path} open failed")
  path = joinPath(".", "signal_nim_inverse2.csv")
  openOk = fp.open(path, fmWrite)
  if openOk:
    defer: fp.close()
    for elem in signal_inv2:
      fp.write(fmt"{elem}")
      fp.write("\n")
  else:
    echo(fmt"{path} open failed")
  pt.leave("output")

if isMainModule:
  var pt = initPhaseTimer()
  pt.enter("indicatorTest")
  main(pt)
  pt.leave("indicatorTest")
# EOF