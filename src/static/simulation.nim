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

var pips* = 0.0001
var loadHistorical_start* = 0
var loadHistorical_end* = 25000

## TODO:OHLCクラスを作る！
# 将来更新される系はObject、更新されないものはTuple
type
  TimeSeries* = seq[DateTime]
  Indicator* = seq[float]
  Candle* = tuple[time:TimeSeries,open:Indicator,high:Indicator,low:Indicator,close:Indicator,volume:Indicator]
  Rolling* = seq[seq[float]]

  Indicators* = Table[string, Indicator]
  KindType* {.pure.} = enum
    take=0,
    release=1,
    invalid=2,
  DirectionType* {.pure.} = enum
    long=1,
    short=2,
    nop=3,
  TradeRecord* = object
    id*: string
    time*: DateTime
    kind*: KindType
    direction*: DirectionType
    point*: float
    unrealizedProfit*: float
    unrealizedLoss*: float
  TradeRecordSeq* = seq[TradeRecord]
  TradeRecordTable* = Table[string, TradeRecordSeq]
  TradePosition* = object
    take*: TradeRecord
    release*: TradeRecord
  TradePositions* = Table[string, TradePosition]
  TradePayOffContents* = tuple
    time: DateTime
    id: string
    benefit: float
    unrealizedProfit: float
    unrealizedLoss: float
  TradePayOff* = seq[TradePayOffContents]

  TakeConditionProc* = proc(candle:Candle, inds:Indicators, itr:int): DirectionType
  ReleaseConditionProc* = proc(candle:Candle, inds:Indicators, itr:int, takeRecord: TradeRecord): DirectionType
  #TradeTactics* = tuple[take:TakeConditionProc, release:ReleaseConditionProc]
  TradeTactics* = object
    take*:TakeConditionProc
    release*:ReleaseConditionProc
  TradeTacticses* = Table[string, TradeTactics]

  ExportTable* = Table[string, string]

proc newIndicators*(): Indicators {.inline.} =
  result = initTable[string, Indicator]()

proc newTradeRecord*(): TradeRecord {.inline.} =
  result = TradeRecord(
    id:"",
    time:parse("19700101 000000", "yyyyMMdd hhmmss", utc()),
    kind: KindType.invalid,
    direction: DirectionType.nop,
    point: 0.0,
    unrealizedProfit: 0.0,
    unrealizedLoss: 0.0
  )
  
proc newTradeRecordTable*(): TradeRecordTable {.inline.} =
  result = initTable[string, TradeRecordSeq]()

proc newTradePositions*(): TradePositions {.inline.} =
  result = initTable[string, TradePosition]()

proc newTradePosition*(): TradePosition {.inline.} =
  result = TradePosition(take: newTradeRecord(), release: newTradeRecord())

proc newTradePayOff*(): TradePayOff {.inline.} =
  result = @[]

proc newTradeTacticss*(): TradeTacticses {.inline.} =
  result = initTable[string, TradeTactics]()

proc newExportTable*(): ExportTable =
  result = initTable[string, string]()


if isMainModule:
  echo("********************\nthis is siimulation.nim.\n********************")
