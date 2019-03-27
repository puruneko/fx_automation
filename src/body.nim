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
loadHistorical_start = 0
loadHistorical_end = 30000
pips = 0.0001

########### trade constant override
trade_spread = 5*pips

###########
proc golden_take(candle: Candle, inds: Indicators, itr: int): DirectionType =
  if itr > 5 and lc[true | (i <- itr-4..itr, inds["mal_div_osc"][i] > 0.12*pips), bool].contains(true):
    if goldenCross(inds["mas"],inds["mal"], itr):
      return DirectionType.long
  return DirectionType.nop

proc golden_release(candle: Candle, inds: Indicators, itr: int, takeRecord: TradeRecord): DirectionType =
  #let madiff = calcPayOff(inds["mal"][itr], candle.close[itr], takeRecord.direction)
  #if madiff <= -3*pips:
  #  return reverseDirection(takeRecord.direction)
  #let mabetween = abs(inds["mas"][itr] - inds["mal"][itr])
  #if mabetween >= 3*pips:
  #  return reverseDirection(takeRecord.direction)
  #let po = calcPayOff(takeRecord.point ,candle.close[itr], takeRecord.direction)
  #if po >= 10*pips or po <= -20*pips:
  #  return reverseDirection(takeRecord.direction)
  let direction = takeRecord.direction
  if direction == DirectionType.long and deadCross(inds["mas"], inds["mal"], itr):
    return DirectionType.short
  return DirectionType.nop

proc dead_take(candle: Candle, inds: Indicators, itr: int): DirectionType =
  if itr > 5 and lc[true | (i <- itr-4..itr, inds["mal_div_osc"][i] < -0.12*pips), bool].contains(true):
    if deadCross(inds["mas"], inds["mal"], itr):
      return DirectionType.short
  return DirectionType.nop

proc dead_release(candle: Candle, inds: Indicators, itr: int, takeRecord: TradeRecord): DirectionType =
  #let madiff = calcPayOff(inds["mal"][itr], candle.close[itr], takeRecord.direction)
  #if madiff <= -5*pips:
  #  return reverseDirection(takeRecord.direction)
  #let mabetween = abs(inds["mas"][itr] - inds["mal"][itr])
  #if mabetween >= 3*pips:
  #  return reverseDirection(takeRecord.direction)
  #let po = calcPayOff(takeRecord.point ,candle.close[itr], takeRecord.direction)
  #if po >= 10*pips or po <= -20*pips:
  #  return reverseDirection(takeRecord.direction)
  let direction = takeRecord.direction
  if direction == DirectionType.short and goldenCross(inds["mas"], inds["mal"], itr):
    return DirectionType.long
  return DirectionType.nop

###############################################################

proc main() =
  echo("---> import start")
  let ohlc = getHistricalData(histricalPath)
  echo(fmt"---| {ohlc[0].len} data found.")
  echo("<--- import end")
  echo("---> settings start")
  let mas = ohlc.close.rolling(30).mean()
  let mal = ohlc.close.rolling(180).mean()
  let mas_div = mal.rolling(2).divide()
  let mal_div = mal.rolling(2).divide()
  var inds: Indicators = newIndicators()
  inds["mas"] = mas
  inds["mal"] = mal
  inds["mas_div_osc"] = mas_div
  inds["mal_div_osc"] = mal_div
  var goldenTrade: TradeCondition
  goldenTrade.name = "goldenTrade"
  goldenTrade.take = golden_take
  goldenTrade.release = golden_release
  var deadTrade: TradeCondition
  deadTrade.name = "deadTrade"
  deadTrade.take = dead_take
  deadTrade.release = dead_release
  var conditions: TradeConditions
  conditions.add(goldenTrade)
  conditions.add(deadTrade)
  echo("<--- settings end")
  echo("---> Simulate start.")
  execTrading(ohlc, inds, conditions, ".")
  echo("<--- Simulate end")


if isMainModule:
  let startTime = cpuTime()
  echo("-> script start")
  main()
  echo("<- script end")
  echo(cpuTime() - startTime,"[s]")