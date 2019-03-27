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
type
  TimeSeries* = seq[DateTime]
  Indicator* = seq[float]
  Candle* = tuple[time:TimeSeries,open:Indicator,high:Indicator,low:Indicator,close:Indicator,volume:Indicator]
  Rolling* = seq[seq[float]]

  Indicators* = Table[string, Indicator]
  KindType* = enum
    take=0,
    release=1,
    invalid=2,
  DirectionType* {.pure.} = enum
    long=1,
    short=2,
    nop=3,
  TradeRecord* = tuple[id: string, time: DateTime, kind: KindType, direction: DirectionType, point: float]#object
  #[
    id: string
    time: DateTime
    kind: KindType
    direction: DirectionType
    point: float
  ]#
  TradeRecordSeq* = seq[TradeRecord]
  TradeRecordTable* = Table[string, TradeRecordSeq]
  TradePosition* = array[2, TradeRecord]
  TradePositions* = Table[string, TradePosition]
  TradePayOff* = seq[tuple[time:DateTime, benefit:float]]

  TakeConditionProc* = proc(candle:Candle, inds:Indicators, itr:int): DirectionType
  ReleaseConditionProc* = proc(candle:Candle, inds:Indicators, itr:int, takeRecord: TradeRecord): DirectionType
  TradeCondition* = object
    name*: string
    take*: TakeConditionProc
    release*: ReleaseConditionProc
  TradeConditions* = seq[TradeCondition]

proc newIndicators*(): Indicators =
  result = initTable[string, Indicator]()

proc newTradeRecordTable*(): TradeRecordTable =
  result = initTable[string, TradeRecordSeq]()

proc newTradePositions*(): TradePositions =
  result = initTable[string, TradePosition]()

proc newTradePosition*(): TradePosition =
  var first: TradePosition
  result = first

proc newTradePayOff*(): TradePayOff =
  result = @[]
