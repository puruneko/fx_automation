eRecord.point, inds["close"][itr], takeRecord.direction)
    if po <= -lossCut:
      if takeRecord.direction == DirectionType.long and inds["close"][itr] < inds["mal"][itr]:
        return reverseDirection(takeRecord.direction)
      if takeRecord.direction == DirectionType.short and inds["close"][itr] > inds["mal"][itr]:
        return reverseDirection(takeRecord.direction)
    if inds["validCrossRange"][itr] != 0.0 and numericCross(inds["forceP_ma"], itr) != 0:
    #if inds["forceIntegral"][itr] == 0*pips:
      return reverseDirectio