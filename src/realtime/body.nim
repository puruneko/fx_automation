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
import "./trade"
import "./tactics"
import "./utils"
import "./extraMath"
import "./phaseTimer"

########### body constant
trade_flag = true
const histricalPath = r"./../../resources/DAT_ASCII_EURUSD_M1_2012.csv"
let loadHistorical_start = 50000
let loadNum = int(25000 * 1.0)
let loadHistorical_end = loadHistorical_start + loadNum

########### simulation constant override
pips = 0.0001

########### trade constant override
tradeSpread = 5*pips

########### tactics constant
let lossCut = 5*pips
let doNotTakePositionNearWindow = true

let maPeriod = 8
let mapPeriod = 32
let masPeriod = 128#180
let mamPeriod = 512
let malPeriod = 1024
let mavPeriod = 4096
let magPeriod = 8192
let divPeriod = 1
let divDivPriod = 4
let smoothPeriod = 128
let smoothDivPeriod = 256
let smoothDivDivPeriod = 256

let mcfsPeriod = 128#64
let mcfmPeriod = 96
let mcflPeriod = 128
let mcfsFilterCoef = 0.05#0.1
let mcfmFilterCoef = 1.0/float(mcfsPeriod)*2.0
let mcflFilterCoef = 1.0/float(mcflPeriod)*2.0
let mcfInterpoleCoef = 1

let divTh = 0.075*pips
let forceIntegral_th = 10000*pips
let shitBf = 1
let shiftAf = 10

let pInd = "mas"
let pInds = [pInd, "mam"]
let pCand = 64
let pIndex = [pCand]
let th = 0.8


############
proc staticIndicator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  return parseFloat(args["value"])

proc maIndicator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  let period = parseInt(args["period"])
  if itr < period:
    return NaN
  return inds[args["targetIndicator"]].rolling(itr, period).ma()

proc maVariableIndicator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  let period = int(parseFloat(args["periodIndicator"]))
  if itr < period:
    return NaN
  return inds[args["targetIndicator"]].rolling(itr, period).ma()

proc maAvgUpperIndicator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  let period = int(parseFloat(args["period"]))
  if itr < period:
    return NaN
  let rl = inds[args["targetIndicator"]].rolling(itr, period)
  let avg = rl.mean()
  let upper = lc[x | (x <- rl, x > avg), float]
  return upper.ma()

proc maAvgLowerIndicator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  let period = int(parseFloat(args["period"]))
  if itr < period:
    return NaN
  let rl = inds[args["targetIndicator"]].rolling(itr, period)
  let avg = rl.mean()
  let lower = lc[x | (x <- rl, x < avg), float]
  return lower.ma()

proc maLogIndicator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  let period = parseInt(args["period"])
  if itr < period:
    return NaN
  return inds[args["targetIndicator"]].rolling(itr, period).uLn().ma().exp()

proc lnIndicator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  return inds[args["targetIndicator"], itr].ln()

proc signedLnIndicator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  return inds[args["targetIndicator"], itr].signedLn()

proc signedExpIndicator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  return inds[args["targetIndicator"], itr].signedExp()

proc doubleIndicator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  return inds[args["targetIndicator"], itr]*inds[args["targetIndicator"], itr]

proc diffOscillator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  return inds[args["targetIndicator1"], itr] - inds[args["targetIndicator2"], itr]

proc lnDivOscillator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  let period = parseInt(args["period"])
  if itr < period:
    return NaN
  let name = args["targetIndicator"]
  return inds[name][itr].ln()-inds[name][itr-period].ln()

proc lnDiffOscillator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  if inds[args["targetIndicator"]][itr].isnull() or inds[args["refIndicator"]][itr].isnull():
    return NaN
  return inds[args["targetIndicator"]][itr].ln()-inds[args["refIndicator"]][itr].ln()

proc divOscillator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  return inds[args["targetIndicator"]].diff(itr, parseInt(args["period"]))

proc divMaxOscillator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  let period = parseInt(args["period"])
  if itr < period:
    return NaN
  return absMax(lc[x-inds[args["targetIndicator"], itr] | (x <- inds[args["targetIndicator"]][itr-period+1..<itr]), float])

proc divSigmaOscillator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  if itr == 0:
    return 0.0
  let diff = inds[args["divOscillator"]][itr]
  return if abs(diff) >= inds[args["sigmaIndicator"]][itr]*parseFloat(args["coef"]): diff
          else: inds[args["selfIndicator"]][itr-1]

proc lowestIndicator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  if itr == 0:
    return inds[args["targetIndicator"], itr]
  if inds[args["selfIndicator"]][itr-1] > inds[args["targetIndicator"], itr]:
    return inds[args["targetIndicator"], itr]
  return inds[args["selfIndicator"]][itr-1] + parseFloat(args["increase"])

proc highestIndicator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  if itr == 0:
    return inds[args["targetIndicator"], itr]
  if inds[args["selfIndicator"]][itr-1] < inds[args["targetIndicator"], itr]:
    return inds[args["targetIndicator"], itr]
  return inds[args["selfIndicator"]][itr-1] - parseFloat(args["decrease"])

proc sigmaIndicator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  return inds[args["targetIndicator"]].rolling(itr, parseInt(args["period"])).sgm()

proc edgeIndicator(inds: ptr Indicators, itr:int, args: IndicatorArgument): float =
  let judgeType = if args.hasKey("judgeType") and args["judgeType"]=="half": "half" else: "full"
  return detectEdge(inds["high"], inds["low"], itr, parseFloat(args["height"])*pips, parseInt(args["width"]), judgeType)

proc mcfIndicator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  return inds["close"].mcf(itr, parseInt(args["period"]), parseFloat(args["filterCoef"]), parseInt(args["interpoleCoef"]))

proc forceOscillator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  let vs = inds[args["targetIndicator1"]][itr]*pow(float(masPeriod), 2.0)
  let vm = inds[args["targetIndicator2"]][itr]*pow(float(mamPeriod), 2.0)
  let vl = inds[args["targetIndicator3"]][itr]*pow(float(malPeriod), 2.0)
  return vs + vm + vl

proc forceMcfOscillator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  let vs = inds["mcfs_div"][itr]*(1.0/mcfsFilterCoef*log2(float(mcfsPeriod)))
  let vm = inds["mcfm_div"][itr]*(1.0/mcfmFilterCoef*log2(float(mcfmPeriod)))
  let vl = inds["mcfl_div"][itr]*(1.0/mcflFilterCoef*log2(float(mcflPeriod)))
  return vs + vm + vl

proc forceIntegralOscillator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  if itr == 0:
    return inds[args["targetIndicator"], itr]
  if inds[args["targetIndicator"]][itr-1] > 0 and inds[args["targetIndicator"], itr] < 0:
    return 0.0
  if inds[args["targetIndicator"]][itr-1] < 0 and inds[args["targetIndicator"], itr] > 0:
    return 0.0
  return inds["forceIntegral"][itr-1] + inds[args["targetIndicator"], itr]

proc forceMcfIntegralOscillator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  if itr == 0:
    return inds["forceMcf"][itr]
  if inds["forceMcf"][itr-1] > 0 and inds["forceMcf"][itr] < 0:
    return 0.0
  if inds["forceMcf"][itr-1] < 0 and inds["forceMcf"][itr] > 0:
    return 0.0
  return inds["forceIntegralMcf"][itr-1] + inds["forceMcf"][itr]

proc limitedSigmaDiffOscillator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  let period = parseInt(args["period"])
  if itr < period:
    return NaN
  let sgmCoef = if args.hasKey("sgmCoef"): parseFloat(args["sgmCoef"]) else: 0.5
  let noBias = inds[args["targetIndicator"]].rolling(itr, period).removeBias()
  let overLimit = noBias.limitedOverSequence(sgmCoef)
  let underLimit = noBias.limitedSequence(sgmCoef)
  if overLimit.len == 0:
    return underLimit.sgm()
  if underLimit.len == 0:
    return overLimit.sgm()
  return overLimit.sgm() - underLimit.sgm()

proc refSigmaDiffOscillator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  let period = parseInt(args["period"])
  if itr < period:
    return NaN
  var diffU: seq[float]
  var diffO: seq[float]
  let sgmCoef = if args.hasKey("sgmCoef"): parseFloat(args["sgmCoef"]) else: 1.5
  let sgmTh = inds[args["targetIndicator"]].rolling(itr, period).sgm()*sgmCoef
  for i in 0..<period:
    let diff = inds[args["targetIndicator"]][itr-period+1+i]-inds[args["refIndicator"]][itr-period+1+i]
    if abs(diff) < sgmTh:
      diffU.add(pow(diff, 1.0))
    else:
      diffO.add(pow(diff, 1.0))
  let refSgmU = sum(diffU)/float(diffU.len)
  let refSgmO = sum(diffO)/float(diffO.len)
  if refSgmU.classify == fcNaN:
    return refSgmO
  if refSgmO.classify == fcNaN:
    return refSgmU
  if refSgmU.classify == fcNaN and refSgmO.classify == fcNaN:
    return 0.0
  return refSgmO - refSgmU

proc rangeCorrelationOscillator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  let period = parseInt(args["period"])
  if itr < period:
    return NaN
  let noTrendIndicator = lc[x[0]-x[1] | (x <- zip(inds[args["targetIndicator"]].rolling(itr, period), inds[args["refIndicator"]].rolling(itr, period))), float]
  let sgmCoef = parseFloat(args["sgmCoef"])
  let rangeWavelet = noTrendIndicator.limitedSequence(sgmCoef)
  return noTrendIndicator.correlation(rangeWavelet)

proc rangeCorrelationVOscillator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  var newArgs = args
  newArgs["period"] = $(int(inds[args["periodIndicator"], itr]))
  return rangeCorrelationOscillator(inds, itr, newArgs)

proc trendCorrelationOscillator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  let period = parseInt(args["period"])
  if itr < period:
    return NaN
  let noTrendIndicator = lc[x[0]-x[1] | (x <- zip(inds[args["targetIndicator"]].rolling(itr, period), inds[args["refIndicator"]].rolling(itr, period))), float]
  let sgmCoef = parseFloat(args["sgmCoef"])
  let rLen = int(period)#inds[args["targetIndicator"]][itr-period+1..itr].limitedSequence(sgmCoef).len
  let maxVal = max(noTrendIndicator)#max(inds[args["targetIndicator"]][itr-rLen+1..itr])
  let minVal = min(noTrendIndicator)#min(inds[args["targetIndicator"]][itr-rLen+1..itr])
  let coef = (maxVal-minVal)/float(rLen)
  let trendWavelet = lc[minVal + float(x)*coef | (x <- 0..<rLen), float]
  return noTrendIndicator.correlation(trendWavelet)

proc trendCorrelationVOscillator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  var newArgs = args
  newArgs["period"] = $(int(inds[args["periodIndicator"], itr]))
  return trendCorrelationOscillator(inds, itr, newArgs)

proc diffSumOscillator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  return (inds["mal", itr]-inds["map", itr])+(inds["mas", itr]-inds["map", itr])+(inds["mam", itr]-inds["map", itr])

proc adjustPeriodIndicator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  let period = parseInt(args["period"])
  if itr < period:
    return float(period)
  let spectrum = inds[args["targetIndicator"]].rolling(itr, period).removeBias().dct().uPow(2.0)
  let sMax = max(spectrum[1..spectrum.len-1])
  let index = spectrum.indexOf(sMax)
  return float(spectrum.len - index)

proc wctIndicator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  let period = parseInt(args["period"])
  if itr < period:
    return NaN
  let pointIndex = int(log2(float(period)))
  let minResolution = 0#int(pow(2.0, float(pointIndex-1)))
  let w = wctImprovement(
          inds[args["targetIndicator"]].rolling(itr, period),
          minResolution,
          proc(t: float):float=pow(sin(t*PI*0.5),4.0)
  )
  let startIndex = int(pow(2.0, float(pointIndex-2)))
  let endIndex = int(pow(2.0, float(pointIndex-1)))
  if w.len < endIndex:
    echo(w.len, "  ", startIndex, "  ", endIndex)
  let ti = args["targetIndicator"]
  for p in 0..<pCand:
    inds[fmt"line_{ti}_{p}", itr] = if abs(w[p]) < th: float(p) else: inds[fmt"line_{ti}_{p}", itr]
  let res = case args["method"]
              of "max": max(w[startIndex..<endIndex])
              of "min": min(w[startIndex..<endIndex])
              of "absMas": absMax(w[startIndex..<endIndex])
              of "absMin": absMin(w[startIndex..<endIndex])
              of "cosMax": max(lc[cos(x*PI*0.5) | (x <- w[startIndex..<endIndex]), float])
              of "mean": mean(w[startIndex..<endIndex])
              else: w[parseInt(args["method"])]
  return res

proc trendDetectionOscirator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  let name = args["name"]
  let target = lc[inds[fmt"wct_max_{name}_{i}"][itr] | (i <- pIndex), float]
  return absMax(target)
proc rangeDetectionOscirator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  let name = args["name"]
  let target = lc[inds[fmt"wct_min_{name}_{i}"][itr] | (i <- pIndex), float]
  return absMin(target)

#
proc validCrossRangeIndicator(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  if itr < 1:
    return 0.0
  let fast = args["fastIndicator"]
  let slow = args["slowIndicator"]
  if numericCross(inds[fast], itr-1) != 0:
    return 0.0
  if inds[fast][itr] < 0 and inds[slow][itr] < 0:
    if goldenCross(inds[fast], inds[slow], itr):
      return 1.0
  if inds[fast][itr] > 0 and inds[slow][itr] > 0:
    if deadCross(inds[fast], inds[slow], itr):
      return -1.0
  return inds[args["selfIndicator"]][itr-1]

proc customBolingerBandClosure(inds: ptr Indicators, itr: int, args: IndicatorArgument): float =
  let centerPeriod = parseInt(args["centerPeriod"])
  let sgmPeriod = parseInt(args["sgmPeriod"])
  if itr < centerPeriod or itr < sgmPeriod:
    return NaN
  let centerRl = inds[args["centerIndicator"]].rolling(itr, centerPeriod)
  let centerAvg = centerRl.mean()
  let centerUpper = lc[x | (x <- centerRl, x > centerAvg), float]
  let centerLower = lc[x | (x <- centerRl, x < centerAvg), float]
  let sgmRl = inds[args["sgmIndicator"]].rolling(itr, sgmPeriod)
  let sgmAvg = sgmRl.mean()
  let sgmUpper = lc[x | (x <- sgmRl, x > sgmAvg), float]
  let sgmLower = lc[x | (x <- sgmRl, x < sgmAvg), float]
  let sgmCoef = parseFloat(args["sgmCoef"])
  inds[args["upperIndicator"], itr] = centerUpper.mean() + sgmUpper.sgm()*sgmCoef
  inds[args["lowerIndicator"], itr] = centerLower.mean() - sgmLower.sgm()*sgmCoef
  return NaN

###########
proc sampleLong_take(inds: ptr Indicators, itr: int): DirectionType =
  let datetime = int(inds["time", itr]).fromUnix().getLocalTime()
  if not (doNotTakePositionNearWindow and datetime.weekday == dFri and datetime.hour == 23):
    if goldenCross(inds["lnd"], inds["band_upper2"], itr):
      return DirectionType.long
  return DirectionType.nop

proc sampleLong_release(inds: ptr Indicators, itr: int, takeRecord: TradeRecord): DirectionType =
  let po = calcPayOff(takeRecord.point, inds["close"][itr], takeRecord.direction)
  if po <= -lossCut:
    if inds["close"][itr] < inds["mal"][itr]:
      return reverseDirection(takeRecord.direction)
  if deadCross(inds["lnd"], inds["band_upper1"], itr):
    return reverseDirection(takeRecord.direction)
  return DirectionType.nop

proc sampleShort_take(inds: ptr Indicators, itr: int): DirectionType =
  let datetime = int(inds["time", itr]).fromUnix().getLocalTime()
  if not (doNotTakePositionNearWindow and datetime.weekday == dFri and datetime.hour == 23):
    if deadCross(inds["lnd"], inds["band_lower2"], itr):
      return DirectionType.short
  return DirectionType.nop

proc sampleShort_release(inds: ptr Indicators, itr: int, takeRecord: TradeRecord): DirectionType =
  let po = calcPayOff(takeRecord.point, inds["close"][itr], takeRecord.direction)
  if po <= -lossCut:
    if inds["close"][itr] > inds["mal"][itr]:
      return reverseDirection(takeRecord.direction)
  if goldenCross(inds["lnd"], inds["band_lower1"], itr):
    return reverseDirection(takeRecord.direction)
  return DirectionType.nop  

###############################################################

proc main(pt: var PhaseTimer) =
  var ohlc: Candle
  var inds: Indicators = newIndicators()
  var conditions: TradeTacticses = newTradeTacticss()
  pt.phase("import"):
    ohlc = getHistricalData(histricalPath, ';', loadHistorical_start, loadHistorical_end)
    echo(fmt"---| {ohlc[0].len} data found.")
  pt.phase("settings"):
    # set indicators
    # arg: indicator proc内で使用される可変パラメータ（指定するときはstring型）
    # stg: indicatorの設定（指定するときはstring型）
    #        display:  グラフに表示するしない（しない：false）
    #        position: グラフのMainウィンドウか否か（main:0, sub:1～）
    #        updateSpecification:  update関数の性質（static：元から用意した配列を使用）
    # ※注意！pushした順番にtrading内で計算されます。
    pt.phase("indicator settings"):
      let timeFloat = lc[float(x.toTime().toUnix()) | (x <- ohlc.time), float]
      inds.push("time", unsafeAddr(timeFloat))
      inds.push("open", unsafeAddr(ohlc.open))
      inds.push("high", unsafeAddr(ohlc.high))
      inds.push("low", unsafeAddr(ohlc.low))
      inds.push("close", unsafeAddr(ohlc.close))
      inds.push("volume", unsafeAddr(ohlc.volume))
      #
      #inds.push("highest", highestIndicator, &&{"targetIndicator": "high", "decrease": $(0.025*pips)}, &&{"display": $true})
      #inds.push("lowest", lowestIndicator, &&{"targetIndicator": "low", "increase": $(0.025*pips)}, &&{"display": $true})
      #inds.push("period", adjustPeriodIndicator, &&{"targetIndicator": "close", "period": $malPeriod}, &&{"display": $true, "position": "1"})
      #
      inds.push("ma", maIndicator, &&{"targetIndicator": "close","period": $maPeriod}, &&{"display": $true})
      inds.push("map", maIndicator, &&{"targetIndicator": "close","period": $mapPeriod}, &&{"display": $true})
      inds.push("mas", maIndicator, &&{"targetIndicator": "close","period": $masPeriod}, &&{"display": $true})
      inds.push("mam", maIndicator, &&{"targetIndicator": "close","period": $mamPeriod}, &&{"display": $true})
      inds.push("mal", maIndicator, &&{"targetIndicator": "close","period": $malPeriod}, &&{"display": $true})
      inds.push("mav", maIndicator, &&{"targetIndicator": "close","period": $mavPeriod}, &&{"display": $true})
      #inds.push("mcfs", mcfIndicator, &&{"period": $mcfsPeriod, "filterCoef": $mcfsFilterCoef, "interpoleCoef": $mcfInterpoleCoef})
      #inds.push("mcfm", mcfIndicator, &&{"period": $mcfmPeriod, "filterCoef": $mcfmFilterCoef, "interpoleCoef": $mcfInterpoleCoef})
      #inds.push("mcfl", mcfIndicator, &&{"period": $mcflPeriod, "filterCoef": $mcflFilterCoef, "interpoleCoef": $mcfInterpoleCoef})
      #
      #inds.push("map_div", divOscillator, &&{"targetIndicator": "map","period": $divPeriod}, &&{"display":"","position": "1"})
      #inds.push("mas_div", divOscillator, &&{"targetIndicator": "mas","period": $divPeriod}, &&{"display": $true,"position": "1"})
      #inds.push("mam_div", divOscillator, &&{"targetIndicator": "mam","period": $divPeriod}, &&{"display": "","position": "1"})
      #inds.push("mal_div", divOscillator, &&{"targetIndicator": "mal","period": $divPeriod}, &&{"display": "","position": "1"})
      #inds.push("mcfs_div", divOscillator, &&{"targetIndicator": "mcfs","period": $divPeriod}, &&{"position": "2", "display": ""})
      #inds.push("mcfm_div", divOscillator, &&{"targetIndicator": "mcfm","period": $divPeriod}, &&{"position": "2", "display": ""})
      #inds.push("mcfl_div", divOscillator, &&{"targetIndicator": "mcfl","period": $divPeriod}, &&{"position": "2", "display": ""})
      #[
      inds.push("forceM", forceOscillator, &&{"targetIndicator1": "mas_div", "targetIndicator2": "mam_div", "targetIndicator3": "mal_div"}, &&{"position":"1","display": ""})
      inds.push("forceM_ma", maIndicator, &&{"targetIndicator": "forceM", "period": $smoothPeriod}, &&{"display": $true,"position":"1"})
      #inds.push("forceP_integral", forceIntegralOscillator, &&{"targetIndicator": "forceM_ma"}, &&{"display": "", "position":"2"})
      inds.push("forceM_div", divOscillator, &&{"targetIndicator": "forceM_ma","period": $divPeriod}, &&{"display": "","position": "2"})
      inds.push("forceM_div_ma", maIndicator, &&{"targetIndicator": "forceM_div", "period": $smoothDivPeriod}, &&{"display": $true,"position":"2"})
      inds.push("forceM_div_div", divOscillator, &&{"targetIndicator": "forceM_div_ma","period": $divPeriod}, &&{"display": "","position": "3"})
      inds.push("forceM_div_div_ma", maIndicator, &&{"targetIndicator": "forceM_div_div", "period": $smoothDivDivPeriod}, &&{"display": "","position":"3"})
      #
      #
      inds.push("forceP", forceOscillator, &&{"targetIndicator1": "map_div", "targetIndicator2": "map_div", "targetIndicator3": "mas_div"}, &&{"position":"1","display": ""})
      inds.push("forceP_ma", maIndicator, &&{"targetIndicator": "forceP", "period": $smoothPeriod}, &&{"display": $true,"position":"1","oppositeAxis": "true"})
      #inds.push("forceP_integral", forceIntegralOscillator, &&{"targetIndicator": "forceP_ma"}, &&{"display": "", "position":"2"})
      inds.push("forceP_div", divOscillator, &&{"targetIndicator": "forceP_ma","period": $divPeriod}, &&{"display": "","position": "2"})
      inds.push("forceP_div_ma", maIndicator, &&{"targetIndicator": "forceP_div", "period": $smoothDivPeriod}, &&{"display": $true,"position":"2","oppositeAxis": "true"})
      inds.push("forceP_div_div", divOscillator, &&{"targetIndicator": "forceP_div_ma","period": $divPeriod}, &&{"display": "","position": "3"})
      inds.push("forceP_div_div_ma", maIndicator, &&{"targetIndicator": "forceP_div_div", "period": $smoothDivDivPeriod}, &&{"display": "","position":"3","oppositeAxis": "true"})
      inds.push("validCrossRange", validCrossRangeIndicator, &&{"fastIndicator":"forceP_ma","slowIndicator":"forceM_ma"}, &&{"display":""})
      #
      #inds.push("upper", maIndicator, &&{"targetIndicator":"close", "period": "4"}, &&{"display": "false"})
      #inds.push("edgeMain", edgeIndicator, &&{"height": fmt"{10*pips}", "width": "10"})
      #inds.push("edgeHalf", edgeIndicator, &&{"height": fmt"{10*pips}", "width": "10", "judgeType": "half"})
      #inds.push("biasC", biasFactorIndicator, &&{"targetIndicator":"mas","period": $mapPeriod}, &&{"display": "", "position": "3", "oppositeAxis": "true"})
      #inds.push("biasP", biasFactorIndicator, &&{"targetIndicator":"mal","period": $mapPeriod}, &&{"display": "", "position": "3"})
      #inds.push("biasC_div", divOscillator, &&{"targetIndicator":"biasC","period": $divPeriod}, &&{"display": "", "position": "3", "oppositeAxis": "true"})
      #inds.push("biasP_div", biasFactorIndicator, &&{"targetIndicator":"biasP","period": $divPeriod}, &&{"display": "", "position": "3"})
      #
      #inds.push("limitedSigmaDiffC", limitedSigmaDiffOscillator, &&{"targetIndicator":"close","period": $masPeriod}, &&{"display": $true, "position": "0", "oppositeAxis": "true"})
      #inds.push("limitedSigmaDiffS", limitedSigmaDiffOscillator, &&{"targetIndicator":"mas","period": $masPeriod}, &&{"display": $true, "position": "0", "oppositeAxis": "true"})
      #inds.push("limitedSigmaDiffL", limitedSigmaDiffOscillator, &&{"targetIndicator":"mal","period": $masPeriod}, &&{"display": $true, "position": "0", "oppositeAxis": "true"})
      inds.push("refSigmaDiffCP", refSigmaDiffOscillator, &&{"targetIndicator":"ma","refIndicator":"map" ,"period": $maPeriod}, &&{"display": "", "position": "0", "oppositeAxis": "true"})
      inds.push("refSigmaDiffCS", refSigmaDiffOscillator, &&{"targetIndicator":"ma","refIndicator":"mas" ,"period": $maPeriod}, &&{"display": "", "position": "0", "oppositeAxis": "true"})
      inds.push("refSigmaDiffPS", refSigmaDiffOscillator, &&{"targetIndicator":"map","refIndicator":"mas" ,"period": $maPeriod}, &&{"display": "", "position": "0", "oppositeAxis": "true"})
      inds.push("refSigmaDiffCP_ma", maIndicator, &&{"targetIndicator":"refSigmaDiffCP","period": $maPeriod}, &&{"display": "", "position": "0", "oppositeAxis": "true"})
      inds.push("refSigmaDiffCS_ma", maIndicator, &&{"targetIndicator":"refSigmaDiffCS","period": $maPeriod}, &&{"display": "", "position": "0", "oppositeAxis": "true"})
      inds.push("refSigmaDiffPS_ma", maIndicator, &&{"targetIndicator":"refSigmaDiffPS","period": $maPeriod}, &&{"display": "", "position": "0", "oppositeAxis": "true"})
      inds.push("refSigmaDiffCP_ma_div", divMaxOscillator, &&{"targetIndicator":"refSigmaDiffCP_ma","period": $mapPeriod}, &&{"display": "", "position": "1", "oppositeAxis": ""})
      inds.push("refSigmaDiffCS_ma_div", divMaxOscillator, &&{"targetIndicator":"refSigmaDiffCS_ma","period": $mapPeriod}, &&{"display": "", "position": "1", "oppositeAxis": ""})
      inds.push("refSigmaDiffPS_ma_div", divMaxOscillator, &&{"targetIndicator":"refSigmaDiffPS_ma","period": $mapPeriod}, &&{"display": "", "position": "1", "oppositeAxis": ""})
      ]#
      ########
      #inds.push("rangeCorrelation", rangeCorrelationOscillator, &&{"targetIndicator": "close", "refIndicator": "map", "period": $malPeriod, "sgmCoef": "0.25"}, &&{"display": "", "position": "0", "oppositeAxis": "true"})
      #inds.push("trendCorrelation", trendCorrelationOscillator, &&{"targetIndicator": "close", "refIndicator": "map", "period": $malPeriod, "sgmCoef": "0.25"}, &&{"display": "", "position": "0", "oppositeAxis": "true"})
      #inds.push("rangeCorrelation_ma", maIndicator, &&{"targetIndicator": "rangeCorrelation", "period": $mamPeriod}, &&{"display": $true, "position": "0", "oppositeAxis": "true"})
      #inds.push("trendCorrelation_ma", maIndicator, &&{"targetIndicator": "trendCorrelation", "period": $mamPeriod}, &&{"display": $true, "position": "0", "oppositeAxis": "true"})
      ########
      #inds.push("rangeCorrelationTest", rangeCorrelationVOscillator, &&{"periodIndicator":"period", "targetIndicator": "close", "refIndicator": "map", "sgmCoef": "0.25"}, &&{"display": "", "position": "0", "oppositeAxis": "true"})
      #inds.push("trendCorrelationTest", trendCorrelationVOscillator, &&{"periodIndicator":"period", "targetIndicator": "close", "refIndicator": "map", "sgmCoef": "0.25"}, &&{"display": "", "position": "0", "oppositeAxis": "true"})
      #inds.push("rangeCorrelationTest_ma", maIndicator, &&{"targetIndicator": "rangeCorrelationTest", "period": $mamPeriod}, &&{"display": $true, "position": "0", "oppositeAxis": "true"})
      #inds.push("trendCorrelationTest_ma", maIndicator, &&{"targetIndicator": "trendCorrelationTest", "period": $mamPeriod}, &&{"display": $true, "position": "0", "oppositeAxis": "true"})
      #
      inds.push(fmt"{th}_position1", staticIndicator, &&{"value": $th}, &&{"display": $true, "position": "0", "oppositeAxis": "true"})
      inds.push(fmt"-{th}_position1", staticIndicator, &&{"value": fmt"-{th}"}, &&{"display": $true, "position": "0", "oppositeAxis": "true"})
      #inds.push(fmt"{th}_position2", staticIndicator, &&{"value": $th}, &&{"display": $true, "position": "1"})
      #inds.push(fmt"-{th}_position2", staticIndicator, &&{"value": fmt"-{th}"}, &&{"display": $true, "position": "1"})
      for pos, name in pInds:
        for p in 0..<pCand:
          inds.pushEmpty(fmt"line_{name}_{p}", &&{"display": "", "position": fmt"{pos+1}"})
      for name in pInds:
        for p in pIndex:
          inds.push(fmt"wct_max_{name}_{p}", wctIndicator, &&{"targetIndicator": name, "period": $p, "method": "16"}, &&{"display": $true, "position": "0", "oppositeAxis": "true"})
          #inds.push(fmt"wct_min_{name}_{p}", wctIndicator, &&{"targetIndicator": name, "period": $p, "method": "cosMax"}, &&{"display": "", "position": "1"})
        #inds.push(fmt"trendDetection_{name}", trendDetectionOscirator, &&{"name": name}, &&{"display": $true, "position": "1"})
        #inds.push(fmt"rangeDetection_{name}", rangeDetectionOscirator, &&{"name": name}, &&{"display": $true, "position": "2"})
      #
      inds.push("lnd", lnDiffOscillator, &&{"targetIndicator": "ma", "refIndicator": "mam"}, &&{"display": $true, "position": "1"})
      inds.push("lnd_ma", maIndicator, &&{"targetIndicator": "lnd", "period": $mamPeriod}, &&{"display": $true, "position": "1"})
      inds.pushEmpty("band_upper1", &&{"display": $true, "position": "1"})
      inds.pushEmpty("band_lower1", &&{"display": $true, "position": "1"})
      inds.pushEmpty("band_upper2", &&{"display": $true, "position": "1"})
      inds.pushEmpty("band_lower2", &&{"display": $true, "position": "1"})
      let bolingerPeriod = malPeriod
      inds.push("bolingerband_closure1", customBolingerBandClosure, &&{"centerIndicator": "lnd_ma", "centerPeriod": $bolingerPeriod, "sgmIndicator": "lnd", "sgmPeriod": $bolingerPeriod, "sgmCoef": "1.0","upperIndicator": "band_upper1", "lowerIndicator": "band_lower1"})
      inds.push("bolingerband_closure2", customBolingerBandClosure, &&{"centerIndicator": "lnd_ma", "centerPeriod": $bolingerPeriod, "sgmIndicator": "lnd", "sgmPeriod": $bolingerPeriod, "sgmCoef": "2.0","upperIndicator": "band_upper2", "lowerIndicator": "band_lower2"})


    # set tactics
    # take: ポジションを取るときの条件関数
    # rekease: ポジションを精算するときの条件関数
    # ※作ったtactics変数はtacticsesに格納する
    pt.phase("tactics settings"):
      var sampleLongTrade = TradeTactics(take: sampleLong_take, release: sampleLong_release)
      var sampleShortTrade = TradeTactics(take: sampleShort_take, release: sampleShort_release)
      conditions["sampleLongTrade"] = sampleLongTrade
      conditions["sampleShortTrade"] = sampleShortTrade
  
  pt.phase("trading"):
    execTrading(ohlc.time, inds, conditions, ".", pt)

if isMainModule:
  let startTime = cpuTime()
  var pt = initPhaseTimer()
  pt.phase("script"):
    main(pt)
  let procTime = cpuTime() - startTime
  recordProcTime(".", procTime)