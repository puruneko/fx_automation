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

type
  WaveletObj* = seq[seq[float]]
  WaveletProc = proc (t: float): float

proc rickerWaveletList(points: int, a: int): seq[float] = #(t: float): float =
  #[
  const s = 1.0
  let a = 2.0 * sqrt(3.0 * s) * pow(PI, 0.25)
  let b = 1.0 - pow((t / s), 2.0)
  let c = pow(E, (-1.0 * t * t / (2.0 * s * s)))
  return a * b * c
  ]#
  let A = 2.0 / (sqrt(3.0 * float(a)) * pow(PI,0.25))
  let wsq = pow(float(a), 2.0)
  var total: seq[float]
  total.newSeq(points)
  for i in 0..<points:
    let vec = float(i) - (float(points) - 1.0) / 2.0
    let xsq = pow(vec,2.0)
    let mod_coef = (1.0 - xsq / wsq)
    let gauss = exp(-xsq / (2.0 * wsq))
    total[i] = A * mod_coef * gauss
  return total


proc meanStatic(sgnl: seq[float]): float {.inline.} =
  sum(sgnl)/float(sgnl.len)

proc adjustAverage(sgnl: seq[float]): seq[float] {.inline.} =
  let avg = meanStatic(sgnl)
  lc[x/avg | (x <- sgnl), float]

proc rickerWavelet(t: float): float {.inline.}=
  const s = 1.0
  let s_inv = 1.0 / s
  let a = 2.0 / (sqrt(3.0 * s) * pow(PI, 0.25))
  let b = 1.0 - pow((t * s_inv), 2.0)
  let c = exp(-1.0 * t * t * s_inv * s_inv * 0.5)
  return a * b * c

proc haarWavelet(t: float): float {.inline.} =
  if 0.0 <= t and t < 1.0:
    return if 0.0 <= t and t < 0.5: 1.0 else: -1.0
  return 0.0

proc cosWavelet(t: float): float {.inline.} =
  cos(t)/sqrt(PI)

proc dwt*(f: Indicator, waveletName: string, tSeq: seq[float], aSeq: seq[float], bSeq: seq[float]): WaveletObj {.inline.}=
  let fLen = f.len
  var dt: seq[float]; dt.newSeq(tSeq.len)
  let waveletList = {"haar":haarWavelet,"ricker":rickerWavelet,"cos":cosWavelet}.toTable()
  let wavelet = waveletList[waveletName]
  for i in 0..<dt.len:
    if i == 0:
      dt[0] = tSeq[1]-tSeq[0]
    else:
      dt[i] = tSeq[i]-tSeq[i-1]
  for itr_a, a in aSeq:
    let a_inv = 1.0/a
    let a_sqrt_inv = 1.0/sqrt(a)
    var res: seq[float]
    res.newSeq(fLen)
    for itr_b, b in bSeq:
      for itr_t in 0..<fLen:#min(itr_a*10+itr_b, fLen):
        res[itr_b] += wavelet((tSeq[itr_t]-b)*a_inv)*f[itr_t]*dt[itr_t]*a_sqrt_inv
    result.add(res)

proc idwt*(wObj: WaveletObj, waveletName: string, tSeq: seq[float], aSeq: seq[float], bSeq: seq[float]): seq[float] {.inline.} =
  let wLen = wObj[0].len
  result.newSeq(wLen)
  let waveletList = {"haar":haarWavelet,"ricker":rickerWavelet,"cos":cosWavelet}.toTable()
  let wavelet = waveletList[waveletName]
  var c: float
  c = 1.0
  var da: seq[float]; da.newSeq(aSeq.len)
  for i in 0..<da.len:
    if i == 0:
      da[0] = aSeq[1]-aSeq[0]
    else:
      da[i] = aSeq[i]-aSeq[i-1]
  var db: seq[float]; db.newSeq(bSeq.len)
  for i in 0..<db.len:
    if i == 0:
      db[0] = bSeq[1]-bSeq[0]
    else:
      db[i] = bSeq[i]-bSeq[i-1]
  for itr_t, t in tSeq:
    var res: seq[float]
    res.newSeq(wObj.len)
    for itr_a, a in aSeq:
      let a_inv = 1.0/a
      let a_sqrt_inv = 1.0/sqrt(a)
      let a_pow2_inv = 1.0/pow(a, 2.0)
      for itr_b, b in bSeq:
        res[itr_a] += wObj[itr_a][itr_b]*wavelet((t-b)*a_inv)*db[itr_b]*a_sqrt_inv*a_pow2_inv
      res[itr_a] *= da[itr_a]
    result[itr_t] = sum(res)#/c

proc processedWaveletObj(w: WaveletObj): WaveletObj =
  let wLen = w.len
  let coefStart = 0.0
  let coefEnd = 0.0
  let itrStart = 0.0
  let itrEnd = 0.3
  let deg = (coefEnd-coefStart)/(itrEnd*float(wLen)-itrStart*float(wLen))
  for itr_a in 0..<wLen:
    var res: seq[float]; res.newSeq(w[itr_a].len)
    if int(itrStart*float(wLen)) <= itr_a and itr_a <= int(itrEnd*float(wLen)):
      for itr_b in 0..<w[itr_a].len:
        res[itr_b] = 0#(w[itr_a][itr_b]/w[itr_a][itr_b]) * abs(w[itr_a][itr_b]) * (coefStart + deg * float(itr_a))
    else:
      let w_itr_a = w[itr_a]
      res = lc[w*1.0/(sum(w_itr_a)/float(w_itr_a.len)) | (w <- w_itr_a), float]
    result.add(res)

proc raisedCosineInterpolation(sgnl: seq[float], padding: int, marginRatio: float = 0.1): seq[float] =
  let marginPoint = int(float(padding) * marginRatio)
  let raisedPoint = padding - marginPoint
  let pf = float(raisedPoint)
  let a = pf * 0.5
  let b = pf * 0.25
  for j in 0..<padding:
    result.add(sgnl[0])
  for i in 1..<sgnl.len:
    for j in 0..<raisedPoint:
      result.add((sgnl[i-1]-sgnl[i]) * (0.5 + 0.5*cos(PI*(float(j)-2.0*b+a)/(2.0*a))) + sgnl[i])
    for j in 0..<marginPoint:
      result.add(sgnl[i])

import "./utils"
proc main(pt: var PhaseTimer) =
  # 準備
  const ohlc_flag = false
  const N = 32
  const P = 32
  const A = 32
  const period = 2
  const wavelet = "haar"
  var signal: seq[float]
  var a: seq[float]
  if ohlc_flag:
    let ohlc = getHistricalData(r"./../../resources/DAT_ASCII_EURUSD_M1_2007.csv", ';', 0, N)
    if P != 0:
      signal = raisedCosineInterpolation(ohlc.close, P)
    else:
      if period <= 1:
        signal = lc[x-meanStatic(ohlc.close) | (x <- ohlc.close), float]
      else:
        for i in 0..<ohlc.close.len:
          if i < period-1:
            signal.add(ohlc.close[0])
          else:
            signal.add(sum(ohlc.close[i-(period-1)..i])/float(period))
    let center = 1.0e-9
    let a_width_rate = 100.0
    #a = lc[exp(float(i)*0.1-float(A/2)) | (i <- 1..A), float]
    a = lc[exp(float(i)*0.25 - float(A/2)) | (i <- 1..A), float]
    #a = lc[float(i) | (i <- 1..A), float]
  else:
    let t = lc[-1.0+float(i)/(float(N)*0.5) | (i <- 0..<N), float]
    let sig_org = lc[cos(2.0 * PI * 7.0 * tt) + sin(PI * 6.0 * tt) | (tt <- t), float]
    if P != 0:
      signal = raisedCosineInterpolation(sig_org, P)
    else:
      signal = sig_org
    a = lc[float(i) | (i <- 1..A), float]
  var b: seq[float] = lc[float(i) | (i <- 0..<signal.len), float]
  var t: seq[float] = lc[float(i) | (i <- 0..<signal.len), float]
  # DWT(単位を全部任意単位に合わせるため、時間tと係数a,bの単位を消す -> 番号で表現) # 本当は t,a,b
  pt.enter("DWT")
  let w = dwt(signal, wavelet, t, a, b)
  pt.leave("DWT")
  # IDWT
  pt.enter("IDWT")
  let signal_inv = idwt(w, wavelet, t, a, b)
  if NaN in signal_inv:
    echo("!!!! NAN detected !!!!")
  pt.leave("IDWT")
  pt.enter("process")
  let w2 = processedWaveletObj(w)
  let signal_inv2 = idwt(w2, wavelet, t, a, b)
  pt.leave("process")
  

  ######
  pt.enter("output")
  var path: string
  var fp: File
  var openOk: bool
  path = joinPath(".", "wavelet.csv")
  openOk = fp.open(path, fmWrite)
  if openOk:
    defer: fp.close()
    for elems in w:
      for index, elem in elems:
        fp.write(fmt"{elem}")
        if index != elems.len-1:
          fp.write(",")
      fp.write("\n")
  else:
    echo(fmt"{path} open failed")
  path = joinPath(".", "wavelet2.csv")
  openOk = fp.open(path, fmWrite)
  if openOk:
    defer: fp.close()
    for elems in w2:
      for index, elem in elems:
        fp.write(fmt"{elem}")
        if index != elems.len-1:
          fp.write(",")
      fp.write("\n")
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