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

var trade_spread* = 5*pips

proc calcPayOff*(takePoint: float, releasePoint: float, pos: DirectionType): float =
  let diff = releasePoint - takePoint
  let pm = if pos == DirectionType.long : 1.0 else : -1.0
  return pm * diff

# take by long at 2016/01/01 00:00:00 at point:1.8000
proc recordTrade(rec: var TradeRecordSeq, pos: var TradePositions,
                  id: string, time: DateTime, kind: KindType, direction: DirectionType, point: float) {.inline.} =
  var tr = (id:id, time:time, kind:kind, direction:direction, point:point)#TradeRecord(id:id, time:time, kind:kind, direction:direction, point:point)
  rec.add(tr)
  pos[id][ord(kind)] = tr

proc payOff(payoff: var TradePayOff, pos: var TradePositions, id: string) =
  let po = calcPayOff(pos[id][KindType.take.ord].point, pos[id][KindType.release.ord].point, pos[id][KindType.take.ord].direction)-trade_spread
  payoff.add((time:pos[id][KindType.release.ord].time, benefit:po))
  pos.del(id)

proc nop(rec: var TradeRecordSeq) =
  var id: string = ""
  var time: DateTime = parse("19700101 000000", "yyyyMMdd hhmmss", utc())
  var kind: KindType = KindType.invalid
  var direction: DirectionType = DirectionType.nop
  var point: float = 0.0
  var empty = (id, time, kind, direction, point)
  rec.add(empty)

proc execTrading*(candle: Candle, inds: Indicators, conditions: TradeConditions, exportPath: string) =
  let tradeLen = candle.time.len
  var tradeRecordTable: TradeRecordTable = newTradeRecordTable()
  var positions: TradePositions = newTradePositions()
  var payoff: TradePayOff = newTradePayOff()
  for condition in conditions:
    tradeRecordTable[condition.name] = @[]
  #############################
  for itr in countup(1, tradeLen-1):
    for condition in conditions:
      if not positions.hasKey(condition.name):
        #if positions[condition.name].take.id == condition.name:
        let take = condition.take(candle, inds, itr) 
        if take != DirectionType.nop:
          positions[condition.name] = newTradePosition()
          recordTrade(tradeRecordTable[condition.name],
                      positions,
                      condition.name,
                      candle.time[itr],
                      KindType.take,
                      take,
                      candle.close[itr])
        else:
          tradeRecordTable[condition.name].nop()
      else:
        let release = condition.release(candle, inds, itr, positions[condition.name][KindType.take.ord])
        if release != DirectionType.nop:
          recordTrade(tradeRecordTable[condition.name],
                      positions,
                      condition.name,
                      candle.time[itr],
                      KindType.release,
                      release,
                      candle.close[itr])
          payOff(payoff, positions, condition.name)
        else:
          tradeRecordTable[condition.name].nop()
  let winPips = sum(lc[po.benefit | (po <- payoff), float])/pips
  let win = (lc[p.benefit | (p <- payOff, p.benefit > 0), float]).len
  echo(fmt"---|")
  echo(fmt"---| RESULT:{winPips}")
  echo(fmt"---|        {win}/{payoff.len}")
  echo(fmt"---|")
  echo("-----> export start")

  #exportData(exportPath, candle, inds, tradeRecordTable, payOff)
  var fp_r: File
  echo("-------> tradeReport.csv start")
  let reportPath = joinPath(exportPath,"tradeReport.csv")
  try:
    var openOk = fp_r.open(reportPath, fmWrite)
    if openOK:
      fp_r.write("date,benefit\n")
      for po in payoff:
        fp_r.write(fmt"{po.time},{po.benefit}")
        fp_r.write("\n")
    else:
      echo(fmt"{reportPath} open failed.")
  except:
    echo(fmt"{reportPath} runtime writting exception.")
  finally:
    fp_r.close()
    echo("<------- tradeReport.csv end")

  echo("-------> tradeHistory.csv start")
  var fp_h: File
  let historyPath = joinPath(exportPath,"tradeHistory.csv")
  try:
    var openOk = fp_h.open(historyPath, fmWrite)
    if openOK:
      const doubleQuate = "\""
      fp_h.write("date,open,high,low,close,volume,")
      for k in inds.keys():
        fp_h.write(fmt"Indicator[{k}],")
      for k in tradeRecordTable.keys():
        fp_h.write(fmt"TradeRecordTable[{k}],")
      fp_h.write("blank\n")
      var outputLine: string = ""
      for itr in countup(2, tradeLen-1):
        outputLine = ""
        #fp_h.write($candle[0][itr] & "," & $candle[1][itr] & "," & $candle[2][itr] & "," & $candle[3][itr] & "," & $candle[4][itr] & "," & $candle[5][itr] & ",")
        outputLine &= fmt"{candle[0][itr]},{candle[1][itr]},{candle[2][itr]},{candle[3][itr]},{candle[4][itr]},{candle[5][itr]},"
        for k in inds.keys():
          outputLine &= fmt"{inds[k][itr]},"
        for kk in tradeRecordTable.keys():
          outputLine &= doubleQuate
          for nm,vl in fieldPairs(tradeRecordTable[kk][itr-1]):
            var nm2 = nm
            var vl2 = vl
            outputLine &= fmt"{nm2}:{vl2},"
          outputLine &= doubleQuate
          outputLine &= ","
        outputLine &= "\n"
        fp_h.write(outputLine)
    else:
      echo(fmt"{historyPath} open failed.")
  except:
    let e = getCurrentExceptionMsg()
    echo(fmt"{historyPath} runtime writting exception.\nMSG: {e}")
  finally:
    fp_h.close()
    echo("<------- tradeHistory.csv end")

  echo("<----- export end")
