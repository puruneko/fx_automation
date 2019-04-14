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

var tradeSpread* = 5*pips

proc calcPayOff*(takePoint: float, releasePoint: float, pos: DirectionType): float =
  let diff = releasePoint - takePoint
  let pm = if pos == DirectionType.long : 1.0 else : -1.0
  return pm * diff

# take by long at 2016/01/01 00:00:00 at point:1.8000
proc recordTrade(rec: var TradeRecordSeq, pos: var TradePositions,
                  id: string, time: DateTime, kind: KindType, direction: DirectionType, point: float) {.inline.} =
  var uProfit = 0.0
  var uLoss = 0.0
  if kind == KindType.release:
    uProfit = pos[id].release.unrealizedProfit
    uLoss = pos[id].release.unrealizedLoss
  var tr = TradeRecord(
    id:id,
    time:time,
    kind:kind,
    direction:direction,
    point:point,
    unrealizedProfit: uProfit,
    unrealizedLoss: uLoss,
  )#TradeRecord(id:id, time:time, kind:kind, direction:direction, point:point)
  rec.add(tr)
  if kind == KindType.take:
    pos[id].take = tr
  if kind == KindType.release:
    pos[id].release = tr

proc updateUnrealizedPoint(pos: var TradePositions, id: string, point: float) {.inline.} =
  var po = calcPayOff(pos[id].take.point, point, pos[id].take.direction)
  if po < 0 and po < pos[id].release.unrealizedLoss:
    pos[id].release.unrealizedLoss = po
  elif po > 0 and po > pos[id].release.unrealizedProfit:
    pos[id].release.unrealizedProfit = po

proc payOff(payoff: var TradePayOff, pos: var TradePositions, id: string): float {.inline.} =
  let po = calcPayOff(pos[id].take.point, pos[id].release.point, pos[id].take.direction)-tradeSpread
  let contents = (
    time: pos[id].release.time,
    id: id,
    benefit: po,
    unrealizedProfit: pos[id].release.unrealizedProfit,
    unrealizedLoss: pos[id].release.unrealizedLoss
  )
  payoff.add(contents)
  pos.del(id)
  return po

proc nop(rec: var TradeRecordSeq) {.inline.} =
  var empty = newTradeRecord()
  rec.add(empty)

proc exportResult(exportPath: string, c: ptr Candle, inds: ptr Indicators, trt: ptr TradeRecordTable, payoff: ptr TradePayOff, et: ptr ExportTable) =
  let tradeLen = c[].close.len
  var fp_r: File
  echo("-------> tradeReport.csv start")
  let reportPath = joinPath(exportPath,"tradeReport.csv")
  try:
    var openOk = fp_r.open(reportPath, fmWrite)
    if openOK:
      fp_r.write("date,id,benefit,unrealizedProfit,unrealizedLoss\n")
      for po in payoff[]:
        fp_r.write(fmt"{po.time},{po.id},{po.benefit},{po.unrealizedProfit},{po.unrealizedLoss}")
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
      for k in inds[].keys():
        if et[].hasKey(k):
          let postfix = if et[][k] == "sub": "*" else: ""
          fp_h.write(fmt"Indicator[{k}]{postfix},")
      for k in trt[].keys():
        for postfix in ["long","short","release"]:
          fp_h.write(fmt"TradeRecordTable[{k}]_{postfix},")
      fp_h.write("blank\n")
      var outputLine: string = ""
      for itr in countup(2, tradeLen-1):
        outputLine = ""
        #fp_h.write($candle[0][itr] & "," & $candle[1][itr] & "," & $candle[2][itr] & "," & $candle[3][itr] & "," & $candle[4][itr] & "," & $candle[5][itr] & ",")
        outputLine &= fmt"{c[][0][itr]},{c[][1][itr]},{c[][2][itr]},{c[][3][itr]},{c[][4][itr]},{c[][5][itr]},"
        for k in inds[].keys():
          if et[].hasKey(k):
            outputLine &= fmt"{inds[][k][itr]},"
        for tr in trt[].values:
          case tr[itr-1].kind:
            of KindType.release:
              outputLine &= fmt",,{tr[itr-1].point},"
            else:
              case tr[itr-1].direction:
                of DirectionType.long:
                  outputLine &= fmt"{tr[itr-1].point},,,"
                of DirectionType.short:
                  outputLine &= fmt",{tr[itr-1].point},,"
                else:
                  outputLine &= fmt",,,"
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

proc execTrading*(candle: Candle, inds: Indicators, conditions: TradeTacticses, exportPath: string, exportTable: ExportTable) =
  let tradeLen = candle.time.len
  var tradeRecordTable: TradeRecordTable = newTradeRecordTable()
  var positions: TradePositions = newTradePositions()
  var payoff: TradePayOff = newTradePayOff()
  for name, condition in conditions.pairs():
    tradeRecordTable[name] = @[]
  #############################
  for itr in countup(1, tradeLen-1):
    for name, condition in conditions.pairs():
      if not positions.hasKey(name):
        #if positions[name].take.id == name:
        let take = condition.take(candle, inds, itr) 
        if take != DirectionType.nop:
          positions[name] = newTradePosition()
          recordTrade(tradeRecordTable[name],
                      positions,
                      name,
                      candle.time[itr],
                      KindType.take,
                      take,
                      candle.close[itr])
        else:
          tradeRecordTable[name].nop()
      else:
        let release = condition.release(candle, inds, itr, positions[name].take)
        if release != DirectionType.nop:
          recordTrade(tradeRecordTable[name],
                      positions,
                      name,
                      candle.time[itr],
                      KindType.release,
                      release,
                      candle.close[itr])
          let benefit = payOff(payoff, positions, name)
          echo(fmt"Paying off has be accomplished![{name}]")
          echo(fmt"    (benefit: {int(benefit/pips)}[pips])(PROGRESS:{int(itr/tradeLen*100)}[%])")
        else:
          updateUnrealizedPoint(positions, name, candle.close[itr])
          tradeRecordTable[name].nop()
  let winPips = sum(lc[po.benefit | (po <- payoff), float])/pips
  let win = (lc[p.benefit | (p <- payOff, p.benefit > 0), float]).len
  echo(fmt"---|")
  echo(fmt"---| RESULT:{winPips}")
  echo(fmt"---|        {win}/{payoff.len}")
  echo(fmt"---|")

  echo("-----> export start")
  exportResult(exportPath, unsafeAddr(candle), unsafeAddr(inds), unsafeAddr(tradeRecordTable), unsafeAddr(payOff), unsafeAddr(exportTable))


if isMainModule:
  echo("********************\nthis is trade.nim.\n********************")