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
import "./indicator"
import "./trade"
import "./tactics"
import "./utils"

########### body constant
const histricalPath = r"./../resources/DAT_ASCII_EURUSD_M1_2007.csv"

########### simulation constant override
loadHistorical_start = 100000
let loadNum = int(25000 * 0.25)
loadHistorical_end = loadHistorical_start + loadNum
pips = 0.0001

########### trade constant override
tradeSpread = 5*pips

########### tactics constant
let masPeriod = 180
let mamPeriod = 600
let malPeriod = 1200
let lossCut = 10*pips
let divTh = 0.075*pips
let shitBf = 1
let shiftAf = 10

###########
proc golden_take(candle: Candle, inds: Indicators, itr: int): DirectionType =
  #if itr > 5 and lc[true | (i <- itr-4..itr, inds["mal_div_osc"][i] > 0.12*pips), bool].contains(true):
  if abs(inds["mas_div"][itr]-inds["mam_div"][itr]) > divTh and inds["mas_div"][itr]>inds["mam_div"][itr]:
    if goldenCrossNearly(inds["mas"],inds["mam"], itr, shitBf, shiftAf):
      return DirectionType.long
  return DirectionType.nop

proc golden_release(candle: Candle, inds: Indicators, itr: int, takeRecord: TradeRecord): DirectionType =
  #let madiff = calcPayOff(inds["mal"][itr], candle.close[itr], takeRecord.direction)
  #if madiff <= -3*pips:
  #  return reverseDirection(takeRecord.direction)
  #let mabetween = abs(inds["mas"][itr] - inds["mal"][itr])
  #if mabetween >= 3*pips:
  #  return reverseDirection(takeRecord.direction)
  let po = calcPayOff(takeRecord.point ,candle.close[itr], takeRecord.direction)
  if po <= -lossCut:
    return reverseDirection(takeRecord.direction)
  if deadCross(inds["mas"],inds["mam"], itr):
    return DirectionType.short
  return DirectionType.nop

proc dead_take(candle: Candle, inds: Indicators, itr: int): DirectionType =
  #if itr > 5 and lc[true | (i <- itr-4..itr, inds["mal_div_osc"][i] < -0.12*pips), bool].contains(true):
  if abs(inds["mas_div"][itr]-inds["mam_div"][itr]) > divTh and inds["mas_div"][itr]<inds["mam_div"][itr]:
    if deadCrossNearly(inds["mas"],inds["mam"], itr, shitBf, shiftAf):
      return DirectionType.short
  return DirectionType.nop

proc dead_release(candle: Candle, inds: Indicators, itr: int, takeRecord: TradeRecord): DirectionType =
  #let madiff = calcPayOff(inds["mal"][itr], candle.close[itr], takeRecord.direction)
  #if madiff <= -5*pips:
  #  return reverseDirection(takeRecord.direction)
  #let mabetween = abs(inds["mas"][itr] - inds["mal"][itr])
  #if mabetween >= 3*pips:
  #  return reverseDirection(takeRecord.direction)
  let po = calcPayOff(takeRecord.point ,candle.close[itr], takeRecord.direction)
  if po <= lossCut:
    return reverseDirection(takeRecord.direction)
  if goldenCross(inds["mas"],inds["mam"], itr):
    return DirectionType.long
  return DirectionType.nop

###############################################################

proc main() =
  echo("---> import start")
  let ohlc = getHistricalData(histricalPath)
  echo(fmt"---| {ohlc[0].len} data found.")
  echo("<--- import end")
  echo("---> settings start")
  # set indicators
  var inds: Indicators = newIndicators()
  inds["upper"] = ohlc.high.ma(4)
  inds["lower"] = ohlc.low.ma(4)
  inds["upper_div"] = inds["upper"].diff(2)
  inds["edgeMain"] = edgeIndicator(ohlc, detectEdge(inds["upper"],inds["lower"],8*pips,8))
  #inds["edgeSub1"] = edgeIndicator(inds["for_edge"], detectEdge(inds["upper"],inds["lower"],8*pips,32))
  inds["edgeHalf"] = edgeIndicator(ohlc, detectHalfEdge(inds["upper"],inds["lower"],8*pips,8))
  inds["mas"] = ohlc.close.ma(masPeriod)
  inds["mam"] = ohlc.close.ma(mamPeriod)
  inds["mal"] = ohlc.close.ma(malPeriod)
  inds["mas_div"] = inds["mas"].diff(2).ma(masPeriod)
  inds["mam_div"] = inds["mam"].diff(2).ma(mamPeriod)
  inds["mal_div"] = inds["mal"].diff(2).ma(malPeriod)
  var exportTable = newExportTable()
  exportTable["upper_div"] = "sub"
  exportTable["edgeMain"] = "main"
  exportTable["edgeHalf"] = "main"
  exportTable["mas"] = "main"
  exportTable["mam"] = "main"
  exportTable["mal"] = "main"
  exportTable["mas_div"] = "sub"
  var goldenTrade = TradeTactics(take:golden_take, release:golden_release)
  var deadTrade = TradeTactics(take: dead_take, release: dead_release)
  var conditions: TradeTacticses = newTradeTacticss()
  conditions["goldenTrade"] = goldenTrade
  conditions["deadTrade"] = deadTrade
  echo("<--- settings end")
  echo("---> Simulate start.")
  execTrading(ohlc, inds, conditions, ".", exportTable)
  echo("<--- Simulate end")


if isMainModule:
  let startTime = cpuTime()
  echo("-> script start")
  main()
  echo("<- script end")
  echo(cpuTime() - startTime,"[s]")