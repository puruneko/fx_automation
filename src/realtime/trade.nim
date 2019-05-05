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
import "./utils"
import "./extraMath"
import "./phaseTimer"

var trade_flag* = true
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

proc exportResult(exportPath: string, time: ptr TimeSeries, inds: ptr Indicators, trt: ptr TradeRecordTable, payoff: ptr TradePayOff) =
  let tradeLen = time[].len
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
      displayError(fmt"{reportPath} open failed.")
  except:
    displayError(fmt"{reportPath} runtime writting exception.")
  finally:
    fp_r.close()
    echo("<------- tradeReport.csv end")

  echo("-------> tradeHistory.csv start")
  let doubleQuate = "\""
  var fp_h: File
  let historyPath = joinPath(exportPath,"tradeHistory.csv")
  try:
    var openOk = fp_h.open(historyPath, fmWrite)
    if openOK:
      const doubleQuate = "\""
      var displayIndicators: seq[string] = @[]
      fp_h.write("date,open,high,low,close,volume,")
      for k in inds[].val.keys():
        if inds[].stg[k].hasKey("display"):
          if inds[].stg[k]["display"].find("true") != -1 or inds[].stg[k]["display"].find("TRUE") != -1:
            displayIndicators.add(k)
            var options = "{"
            for key, value in inds[].stg[k].pairs():
              if key == "display":
                continue
              options &= fmt"{key}:{value},"
            options &= "}"
            fp_h.write(fmt"{doubleQuate}Indicator[{k}]{options}{doubleQuate},")
      for k in trt[].keys():
        let bracket = "{}"
        for postfix in ["long","short","release"]:
          fp_h.write(fmt"TradeRecordTable[{k}]_{postfix}{bracket},")
      fp_h.write("blank\n")
      var outputLine = ""
      for itr in countup(1, tradeLen-1):
        outputLine = ""
        #fp_h.write($candle[0][itr] & "," & $candle[1][itr] & "," & $candle[2][itr] & "," & $candle[3][itr] & "," & $candle[4][itr] & "," & $candle[5][itr] & ",")
        outputLine &= fmt"{time[][itr]},"
        for label in ["open","high","low","close","volume"]:
          outputLine &= fmt"{inds[].val[label][itr]},"
        for k in inds[].val.keys():
          if displayIndicators.contains(k):
            outputLine &= fmt"{inds[].val[k][itr]},"
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
      displayError(fmt"{historyPath} open failed.")
  except:
    let e = getCurrentExceptionMsg()
    displayError(fmt"{historyPath} runtime writting exception.\nMSG: {e}")
  finally:
    fp_h.close()
    echo("<------- tradeHistory.csv end")

  echo("<----- export end")

proc execTrading*(time: TimeSeries, inds: var Indicators, conditions: TradeTacticses, exportPath: string, pt: PhaseTimer) =
  let tradeLen = time.len
  var tradeRecordTable: TradeRecordTable = newTradeRecordTable()
  var positions: TradePositions = newTradePositions()
  var payoff: TradePayOff = newTradePayOff()
  for name, condition in conditions.pairs():
    tradeRecordTable[name] = @[]
  #############################
  try:
    for itr in countup(0, tradeLen-1):
      # インジケータのアップデート
      updateAll(unsafeAddr(inds), itr)
      for name, condition in conditions.pairs():
        # ポジションがない場合
        if not positions.hasKey(name):
          if trade_flag:
            # ポジションを取れる条件下か計算
            let take = condition.take(unsafeAddr(inds), itr)
            # ポジションを取れる場合
            if take != DirectionType.nop:
              # 新しいポジションの作成
              positions[name] = newTradePosition()
              # ポジションの記録
              recordTrade(tradeRecordTable[name],
                          positions,
                          name,
                          time[itr],
                          KindType.take,
                          take,
                          inds.val["close"][itr])
              pt.msg(fmt"take position[{name}]")
            else:
              tradeRecordTable[name].nop()
          else:
            tradeRecordTable[name].nop()
        else:
          let release = condition.release(unsafeAddr(inds), itr, positions[name].take)
          if release != DirectionType.nop:
            recordTrade(tradeRecordTable[name],
                        positions,
                        name,
                        time[itr],
                        KindType.release,
                        release,
                        inds.val["close"][itr])
            let benefit = payOff(payoff, positions, name)

            pt.msg(fmt"release position[{name}](benefit: {int(benefit/pips)}[pips])")
          else:
            updateUnrealizedPoint(positions, name, inds.val["close"][itr])
            tradeRecordTable[name].nop()
      if itr mod int(tradeLen/10) == 0:
        let percentage = int(itr/tradeLen*100)
        pt.msg(fmt"PROGRESS:{percentage} [%]", true)
  except:
    echo("!!! catch in execTrade !!!\n", getCurrentExceptionMsg())
    raise getCurrentException()
  let winPips = sum(lc[po.benefit | (po <- payoff), float])/pips
  let win = (lc[p.benefit | (p <- payOff, p.benefit > 0), float]).len
  pt.msg("")
  let msg = fmt"RESULT:{winPips}{'\n'}{' '.repeat(13)}{win}/{payoff.len}{'\n'}{' '.repeat(13)}{tradeLen} poins has be analysed."
  pt.msg(msg)
  pt.msg("")

  echo("-----> export start")
  exportResult(exportPath, unsafeAddr(time), unsafeAddr(inds), unsafeAddr(tradeRecordTable), unsafeAddr(payOff))


if isMainModule:
  echo("********************\nthis is trade.nim.\n********************")