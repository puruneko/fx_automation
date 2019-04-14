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

type
  Edge = tuple[direction: DirectionType, itr: int]
  Edges = seq[Edge]

proc detectEdge*(upper: Indicator, lower: Indicator, edgeUnitHeight: float, edgeUnitHalfNum: int): Edges =
  let cLen = upper.len
  for itr in edgeUnitHalfNum..<cLen-edgeUnitHalfNum:
    # long
    if upper[itr] >= max(upper[(itr-edgeUnitHalfNum)..(itr+edgeUnitHalfNum)]):
      if (upper[itr]-min(lower[(itr-edgeUnitHalfNum)..<itr])) > edgeUnitHeight:
        if (upper[itr]-min(lower[(itr+1)..(itr+edgeUnitHalfNum)])) > edgeUnitHeight:
          echo(fmt"  +add {itr}")
          result.add((direction: DirectionType.long, itr: itr))
    elif lower[itr] <= min(lower[(itr-edgeUnitHalfNum)..(itr+edgeUnitHalfNum)]):
      if (max(upper[(itr-edgeUnitHalfNum)..<itr])-lower[itr]) > edgeUnitHeight:
        if (max(upper[(itr+1)..(itr+edgeUnitHalfNum)])-lower[itr]) > edgeUnitHeight:
          result.add((direction: DirectionType.short, itr: itr))
          echo(fmt"  -add {itr}")

proc detectHalfEdge*(upper: Indicator, lower: Indicator, edgeUnitHeight: float, edgeUnitHalfNum: int): Edges =
  let cLen = upper.len
  for itr in edgeUnitHalfNum..<cLen-edgeUnitHalfNum:
    # long
    if upper[itr] >= max(upper[(itr-edgeUnitHalfNum)..(itr+edgeUnitHalfNum)]):
      if (upper[itr]-min(upper[(itr-edgeUnitHalfNum)..<itr])) > edgeUnitHeight or (upper[itr]-min(upper[(itr+1)..(itr+edgeUnitHalfNum)])) > edgeUnitHeight:
          echo(fmt"  +halfAdd {itr}")
          result.add((direction: DirectionType.long, itr: itr))
    elif lower[itr] <= min(lower[(itr-edgeUnitHalfNum)..(itr+edgeUnitHalfNum)]):
      if (max(lower[(itr-edgeUnitHalfNum)..<itr])-lower[itr]) > edgeUnitHeight or (max(lower[(itr+1)..(itr+edgeUnitHalfNum)])-lower[itr]) > edgeUnitHeight:
          result.add((direction: DirectionType.short, itr: itr))
          echo(fmt"  -halfAdd {itr}")

proc edgeIndicator*(candle: Candle, edges: Edges): Indicator =
  var eItr = 0
  for itr in 0..<candle.close.len:
    if eItr < edges.len and edges[eItr].itr == itr:
      if edges[eItr].direction == DirectionType.long:
        result.add(candle.high[itr])
      else:
        result.add(candle.low[itr])
      inc(eItr)
    else:
      result.add(NaN)

proc rolling*(ind: Indicator, period: int): Rolling =
  for i in countup(0,period-1):
    result.add(@[])
  for i in countup(0,ind.len-period-1):
    result.add(ind[i..<(i+period)])

proc mean*(rolling: Rolling): Indicator =
  for rl in rolling:
    if NaN in rl or rl.len == 0:
      result.add(NaN)
    else:
      result.add(sum(rl)/float(rl.len))

proc divide*(rolling: Rolling): Indicator =
  for rl in rolling:
    if NaN in rl or rl.len == 0:
      result.add(NaN)
    else:
      result.add((rl[rl.len-1]-rl[0])/float(rl.len-1))

proc ma*(ind: Indicator, period: int): Indicator =
  return ind.rolling(period).mean()

proc diff*(ind: Indicator, period: int): Indicator =
  return ind.rolling(period).divide()