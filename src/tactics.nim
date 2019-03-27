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

proc reverseDirection*(direction: DirectionType): DirectionType =
  result = case direction:
    of DirectionType.long: DirectionType.short
    of DirectionType.short: DirectionType.long
    else: DirectionType.nop

proc goldenCross*(ind1, ind2: Indicator, itr: int): bool =
  if ind1[itr-1] < ind2[itr-1] and ind1[itr] >= ind2[itr]:
    return true
  return false

proc deadCross*(ind1, ind2: Indicator, itr: int): bool =
  if ind1[itr-1] > ind2[itr-1] and ind1[itr] <= ind2[itr]:
    return true
  return false
  