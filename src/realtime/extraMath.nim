import sugar
import math

proc direction*(a: float, b: float): int =
  if float(a) != float(b): int((b-a)/abs(b-a)) else: 0

proc adjustFigure*(x: float, figure: float = 0.0): float =
  if x == 0.0:
    return 0.0
  return x * pow(10.0, -log10(x).floor) * pow(10.0, figure)

proc sign*(x: float): float =
  x/abs(x)

proc sign*(x: int): int =
  int(float(x)/float(abs(x)))

proc meanStatic*(sgnl: seq[float]): float {.inline.} =
  sum(sgnl)/float(sgnl.len)

proc adjustPower*(sig: seq[float], ref_sig: seq[float]): seq[float] =
  let coef1 = sqrt(meanStatic(lc[x*x | (x <- sig), float]))
  let coef2 = sqrt(meanStatic(lc[x*x | (x <- ref_sig), float]))
  return lc[x*coef2/coef1 | (x <- sig), float]
  
###############################
proc logE*(x: float): float =
  return log(x, E)

###############################
proc uLn*(sequence: seq[float]): seq[float] =
  lc[log(x, E) | (x <- sequence), float]

proc uLog2*(sequence: seq[float]): seq[float] =
  lc[log2(x) | (x <- sequence), float]

proc uLog10*(sequence: seq[float]): seq[float] =
  lc[log10(x) | (x <- sequence), float]

proc uExp*(sequence: seq[float]): seq[float] =
  lc[exp(x) | (x <- sequence), float]

proc uSqrt*(sequence: seq[float]): seq[float] =
  lc[sqrt(x) | (x <- sequence), float]

###############################
proc signedSqrt*(x: float): float =
  return sign(x) * sqrt(abs(x))

proc signedLog10*(x: float): float =
  return sign(x) * log10(abs(x))

proc signedLn*(x: float): float =
  return sign(x) * ln(abs(x))

###############################
proc absMax*(x: openArray[float]): float =
  result = -Inf
  for y in x:
    if result < abs(y):
      result = y

proc absMin*(x: openArray[float]): float =
  result = +Inf
  for y in x:
    if result > abs(y):
      result = y
