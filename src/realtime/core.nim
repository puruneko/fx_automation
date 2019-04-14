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

############ variable constant (they will be overriden)
var pips* = 0.0001
var loadHistorical_start* = 0
var loadHistorical_end* = 25000

############ static constant
let emptySetting* = initTable[string, string]()
let emptyArgument* = initTable[string, string]()

## TODO:OHLCクラスを作る！
# 将来更新される系はObject、更新されないものはTuple
type
  TimeSeries* = seq[DateTime]
  
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

  Indicator* = seq[float]
  IndicatorArgument* = Table[string, string]
  IndicatorProc* = proc (indicators: Indicators, itr: int, args: IndicatorArgument): float
  IndicatorSettings* = Table[string, string]
  Indicators* = object
    val*: OrderedTable[string, Indicator]
    prc*: OrderedTable[string, IndicatorProc]
    arg*: OrderedTable[string, IndicatorArgument]
    stg*: OrderedTable[string, IndicatorSettings]
    adr*: Table[string, ptr Indicator]

  Candle* = tuple[time:TimeSeries,open:Indicator,high:Indicator,low:Indicator,close:Indicator,volume:Indicator]

  TradePayOffContents* = tuple
    time: DateTime
    id: string
    benefit: float
    unrealizedProfit: float
    unrealizedLoss: float
  TradePayOff* = seq[TradePayOffContents]

  TakeConditionProc* = proc(inds:Indicators, itr:int): DirectionType
  ReleaseConditionProc* = proc(inds:Indicators, itr:int, takeRecord: TradeRecord): DirectionType
  #TradeTactics* = tuple[take:TakeConditionProc, release:ReleaseConditionProc]
  TradeTactics* = object
    take*: TakeConditionProc
    release*: ReleaseConditionProc
  TradeTacticses* = Table[string, TradeTactics]

  ExportTable* = Table[string, string]

###########
proc `&&`*[T,U](pair: openArray[(T,U)]): Table[T,U] =
  pair.toTable

###########
proc newIndicator*(): Indicator =
  result = @[]

### Indicators class method
proc newIndicators*(): Indicators =
  result.val = initOrderedTable[string, Indicator]()
  result.prc = initOrderedTable[string, IndicatorProc]()
  result.arg = initOrderedTable[string, IndicatorArgument]()
  result.stg = initOrderedTable[string, IndicatorSettings]()
  result.adr = initTable[string, ptr Indicator]()

proc `[]`*(inds: Indicators, label: string): Indicator =
  return inds.val[label]
  
# dynamic
method push*(self: var Indicators, id: string, prc: IndicatorProc, arg: IndicatorArgument = emptyArgument, stg: IndicatorSettings = emptySetting): Indicators {.discardable.} =
  self.val[id] = newIndicator()
  self.prc[id] = prc
  self.arg[id] = arg
  self.arg[id]["selfIndicator"] = id
  self.stg[id] = stg

# static
method push*(self: var Indicators, id: string, adr: ptr Indicator, stg: IndicatorSettings = emptySetting): Indicators{.discardable.} =
  self.val[id] = newIndicator()
  self.adr[id] = adr
  self.stg[id] = stg
  self.stg[id]["updateSpecification"] = "static"

method del*(self: var Indicators, id: string) =
  self.val.del(id)
  self.prc.del(id)
  self.stg.del(id)
  if self.adr.hasKey(id):
    self.adr.del(id)

method addSettings*(self: var Indicators, id: string, stg: IndicatorSettings) =
  for key, value in stg.pairs():
    self.stg[id][key] = value

method update(self: var Indicators, id: string, itr: int, args: IndicatorArgument) =
  self.val[id].add(self.prc[id](self, itr, args))

method updateStatic(self: var Indicators, id: string, adr: ptr Indicator, itr: int) =
  self.val[id].add(adr[][itr])

method updateAll*(self: var Indicators, itr: int) =
  for key in self.val.keys():
    if self.stg[key].hasKey("updateSpecification") and self.stg[key]["updateSpecification"] == "static":
      self.updateStatic(key, self.adr[key], itr)
    else:
      self.update(key, itr, self.arg[key])

###########
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