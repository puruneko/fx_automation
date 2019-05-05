import sugar
import math
import strformat

proc direction*(a: float, b: float): int =
  if float(a) != float(b): int((b-a)/abs(b-a)) else: 0

proc adjustFigure*(x: float, figure: float = 0.0): float =
  if x == 0.0:
    return 0.0
  return x * pow(10.0, -log10(x).floor) * pow(10.0, figure)

proc sign*(x: float): float =
  x/abs(x)

proc sign*(x: int): int =
  int(float(x)/float(abs(x)))

proc mean*(sgnl: seq[float]): float =
  sum(sgnl)/float(sgnl.len)

proc adjustPower*(sig: seq[float], ref_sig: seq[float]): seq[float] =
  let coef1 = sqrt(mean(lc[x*x | (x <- sig), float]))
  let coef2 = sqrt(mean(lc[x*x | (x <- ref_sig), float]))
  return lc[x*coef2/coef1 | (x <- sig), float]

proc isnull*(x: float): bool =
  return not (x.classify == fcNormal or x.classify == fcZero or x.classify == fcSubnormal)

###############################
proc sgm2*(sequence: seq[float]): float =
  let avg = sequence.mean()
  return mean(lc[pow((x-avg), 2.0) | (x <- sequence), float])

proc sgm*(sequence: seq[float]): float =
  return sqrt(sequence.sgm2())

proc correlation*(longer: seq[float], shorter: seq[float], adjust: bool = true): float =
  let longer2 = longer[longer.len-shorter.len..<longer.len]
  let shorter2 = if adjust: adjustPower(shorter, longer2) else: shorter
  let longerAvg = longer2.mean()
  let shorterAvg = shorter2.mean()
  let longerSgm = longer2.sgm()
  let shorterSgm = shorter2.sgm()
  let mother = longerSgm*shorterSgm
  for i in 0..<shorter2.len:
    result += (longer2[i]-longerAvg)*(shorter2[i]-shorterAvg)
  result /= float(shorter2.len)*mother

###############################
proc uLn*(sequence: seq[float]): seq[float] =
  lc[log(x, E) | (x <- sequence), float]

proc uLog2*(sequence: seq[float]): seq[float] =
  lc[log2(x) | (x <- sequence), float]

proc uLog10*(sequence: seq[float]): seq[float] =
  lc[log10(x) | (x <- sequence), float]

proc uExp*(sequence: seq[float]): seq[float] =
  lc[exp(x) | (x <- sequence), float]

proc uSqrt*(sequence: seq[float]): seq[float] =
  lc[sqrt(x) | (x <- sequence), float]

proc uPow*(sequence: seq[float], y: float): seq[float] =
  lc[pow(x, y) | (x <- sequence), float]

###############################
proc signedSqrt*(x: float): float =
  return sign(x) * sqrt(abs(x))

proc signedExp*(x: float): float =
  return sign(x) * exp(abs(x))

proc signedLog10*(x: float): float =
  return sign(x) * log10(abs(x))

proc signedLn*(x: float): float =
  return sign(x) * ln(abs(x))

###############################
proc absMax*(x: openArray[float]): float =
  var res = -Inf
  for y in x:
    if abs(res) < abs(y):
      res = y
  return res

proc absMin*(x: openArray[float]): float =
  var res = +Inf
  for y in x:
    if abs(res) > abs(y):
      res = y
  return res

###############################
proc raisedCosine*(starts: float, ends: float, N: int): seq[float] =
  result.newSeq(N)
  let a = float(N) * 0.5
  let b = float(N) * 0.25
  for i in 0..<N:
    result[i] = (starts-ends) * (0.5 + 0.5*cos(PI*(float(i)-2.0*b+a)/(2.0*a))) + ends
proc raisedCosineInterpolation*(sgnl: seq[float], padding: int, marginRatio: float = 0.1): seq[float] =
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
proc raisedCosineInterpolation2*(sgnl: seq[float], padding: int, margin: float =0.1): seq[float] =
  let margin_point = int(float(padding) * margin)
  var dir = direction(sgnl[0], sgnl[1])
  var dir_now: int
  var itr_start = 0
  var counter = 1
  #for j in range(padding):
  #  result.append(sgnl[0])
  for i in 1..<sgnl.len:
    dir_now = direction(sgnl[i-1], sgnl[i])
    if dir_now == dir:
      counter += 1
    elif dir_now != dir or dir_now == 0:
      let point = padding*counter
      for r in raisedCosine(sgnl[itr_start], sgnl[i-1], point-margin_point):
        result.add(r)
      for j in 0..<margin_point:
        result.add(sgnl[i-1])
      dir = dir_now
      counter = 1
      itr_start = i-1
  let i = len(sgnl)-1
  let point = padding*(counter)
  for r in raisedCosine(sgnl[itr_start], sgnl[i], point-margin_point):
    result.add(r)
  for j in 0..<margin_point:
    result.add(sgnl[i])
proc wFilter*(w: seq[float], th: int = 16): seq[float] =
  # 低周波だけ残す
  let wLen = w.len
  result.newSeq(wLen)
  for i in 0..<wLen:
    if th <= i:
      result[i] = 0
    else:
      result[i] = w[i]
proc dct*(ind: seq[float]): seq[float] =
  let N = float(ind.len)
  result.newSeq(int(N))
  let coef = sqrt(2.0/N)
  for itr_k in 0..<int(N):
    let k = float(itr_k)
    for itr_n in 0..<int(N):
      result[itr_k] += coef*ind[itr_n]*cos(PI/N*(float(itr_n)+0.5)*k)

proc idct*(ind: seq[float]): seq[float] =
  let N = float(ind.len)
  result.newSeq(int(N))
  let coef = sqrt(2.0/N)
  for itr_k in 0..<int(N):
    let k = float(itr_k)
    for itr_n in 0..<int(N):
      result[itr_k] += coef*ind[itr_n]*cos(PI/N*float(itr_n)*(k+0.5))

proc mcf*(ind: seq[float], itr: int, period: int, filterCoef: float = 0.125, interpoleCoef: int = 4): float =
  # moving cosine filter
  if itr < period:
    return NaN
  let filterNum = int(float(period)*filterCoef)
  let signal = raisedCosineInterpolation2(ind[itr-period..itr], interpoleCoef)
  return adjustPower(idct(wFilter(dct(signal), filterNum)), signal)[^1]

proc removeBias*(ind: seq[float]): seq[float] =
  let mean = ind.mean()
  return lc[x - mean | (x <- ind), float]

import os
proc wct*(ind: seq[float], maxHeight: float, heightPoint: int, minWidthPoint: int, waveletProc: proc(t: float): float): seq[seq[float]] =
  # wavelet correlation transform
  # 基本waveletは縦0..1、横0..1に正規化されているものとする
  # heightHalfを最大値として縦方向に拡大縮小して相関係数を計算
  # widthHalfを最大値として横方向に拡大縮小して相関係数を計算
  try:
    result.newSeq(heightPoint+1)
    let pips = 0.0001
    let ind2 = lc[x/pips | (x <- ind.removeBias()), float]
    let dh = maxHeight/pips/float(heightPoint)
    let trueLen = ind2.len-minWidthPoint
    result[0].newSeq(trueLen)
    for itr_h in 1..heightPoint:
      result[itr_h].newSeq(trueLen)
      for itr_w in minWidthPoint..<ind2.len:
        var wavelet: seq[float]
        for itr_t in 0..itr_w:
          wavelet.add(waveletProc(float(itr_t)/float(itr_w))*float(itr_h)*dh-float(itr_h/2)*dh)
        result[itr_h][itr_w-minWidthPoint] = correlation(ind2, wavelet)
  except:
    echo(getCurrentExceptionMsg())
    raise getCurrentException()

proc wctImprovement*(ind: seq[float], minWidthPoint: int, waveletProc: proc(t: float): float): seq[float] =
  let w = wct(ind, 1, 1, minWidthPoint, waveletProc)
  return w[1]

import "./utils"
import "./phaseTimer"
proc main(pt: var PhaseTimer) =
  const N = 128
  const M = 128
  var fp: File
  var openOk: bool
  var path: string
  path = joinPath(".", "wct_signal_" & $N & ".csv")
  openOk = fp.open(path, fmWrite)
  fp.close()
  path = joinPath(".", "wct_result_" & $N & ".csv")
  openOk = fp.open(path, fmWrite)
  fp.close()
  path = joinPath(".", "wct_maxmin_" & $N & ".csv")
  openOk = fp.open(path, fmWrite)
  fp.close()
  path = joinPath(".", "wct_cos4_" & $N & ".csv")
  openOk = fp.open(path, fmWrite)
  fp.close()
  pt.phase("WCT"):
    for i in 0..M:
      let START = i
      let END = START + N
      let ohlc = getHistricalData(r"./../../resources/DAT_ASCII_EURUSD_M1_2007.csv", ';', START, END)
      let close = ohlc[4]
      let maxHeight = close.removeBias().max()
      let minPoint = 4
      let w = wctImprovement(close, minPoint, proc(t: float):float=pow(sin(t*PI*0.5), 4.0))
      let w2 = lc[pow(cos(x*PI*0.5), 1.0) | (x <- w), float]

      path = joinPath(".", "wct_signal_" & $N & ".csv")
      openOk = fp.open(path, fmAppend)
      if openOk:
        defer: fp.close()
        fp.write($i & ",")
        for elem in close:
          fp.write($elem & ",")
        fp.write("\n")
      else:
        echo($path & " open failed")
      path = joinPath(".", "wct_result_" & $N & ".csv")
      openOk = fp.open(path, fmAppend)
      if openOk:
        defer: fp.close()
        fp.write($i & ",")
        for elem in w:
          fp.write($elem & ",")
        fp.write("\n")
      else:
        echo($path & " open failed")
      path = joinPath(".", "wct_cos4_" & $N & ".csv")
      openOk = fp.open(path, fmAppend)
      if openOk:
        defer: fp.close()
        fp.write($i & ",")
        for elem in w2:
          fp.write($elem & ",")
        fp.write("\n")
      else:
        echo($path & " open failed")
      path = joinPath(".", "wct_maxmin_" & $N & ".csv")
      openOk = fp.open(path, fmAppend)
      if openOk:
        defer: fp.close()
        let m = int(log2(float(N)))
        fp.write($i & ",")
        fp.write($(max(w[0..<int(pow(2.0,float(3)))])) & ",")
        fp.write($(min(w[0..<int(pow(2.0,float(3)))])) & ",")
        for j in 3..<m:
          fp.write($(max(w[int(pow(2.0,float(j)))..<int(pow(2.0,float(j+1)))])) & ",")
          fp.write($(min(w[int(pow(2.0,float(j)))..<int(pow(2.0,float(j+1)))])) & ",")
        fp.write("\n")
      else:
        echo($path & " open failed")


if isMainModule:
  var pt = initPhaseTimer()
  pt.phase("extraMath"):
    main(pt)