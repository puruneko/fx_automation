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
