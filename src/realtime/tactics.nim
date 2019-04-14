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

proc reverseDirection*(direction: DirectionType): DirectionType =
  result = case direction:
    of DirectionType.long: DirectionType.short
    of DirectionType.short: DirectionType.long
    else: DirectionType.nop

proc goldenCross*(ind1, ind2: Indicator, itr: int): bool =
  if itr < 1:
    return false
  if ind1[itr-1] < ind2[itr-1] and ind1[itr] >= ind2[itr]:
    return true
  return false

proc deadCross*(ind1, ind2: Indicator, itr: int): bool =
  if itr < 1:
    return false
  if ind1[itr-1] > ind2[itr-1] and ind1[itr] <= ind2[itr]:
    return true
  return false
  
proc goldenCrossNearly*(ind1, ind2: Indicator, itr: int, shiftBf=1, shiftAf=1, fixed=[false,true]): bool =
  if shiftBf > itr:
    return false
  var slope1 = (ind1[itr]-ind1[itr-shiftBf])/float(shiftBf)
  var slope2 = (ind2[itr]-ind2[itr-shiftBf])/float(shiftBf)
  var next1 = if fixed[0]: ind1[itr] else: ind1[itr] + slope1 * float(shiftAf)
  var next2 = if fixed[1]: ind2[itr] else: ind2[itr] + slope1 * float(shiftAf)
  if ind1[itr] < ind2[itr] and next1 >= next2:
    return true
  return false

proc deadCrossNearly*(ind1, ind2: Indicator, itr: int, shiftBf=1, shiftAf=1, fixed=[false,true]): bool =
  if shiftBf > itr:
    return false
  var slope1 = (ind1[itr]-ind1[itr-shiftBf])/float(shiftBf)
  var slope2 = (ind2[itr]-ind2[itr-shiftBf])/float(shiftBf)
  var next1 = if fixed[0]: ind1[itr] else: ind1[itr] + slope1 * float(shiftAf)
  var next2 = if fixed[1]: ind2[itr] else: ind2[itr] + slope1 * float(shiftAf)
  if ind1[itr] > ind2[itr] and next1 <= next2:
    return true
  return false

proc numericCross*(ind: Indicator, itr: int, numeric: float = 0.0): int =
  if itr < 1:
    return 0
  if ind[itr-1] <= numeric and ind[itr] > numeric:
    return 1
  elif ind[itr-1] >= numeric and ind[itr] < numeric:
    return -1
  return 0