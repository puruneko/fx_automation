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

type
  Matrix* = object
    val*: seq[float]
    row*: int
    col*: int
  MatrixException* = object of Exception

################ inner proc ################
method getIndexNumber(mt: Matrix, index: array[2, int]): int {.base.} =
  let num = index[1] + index[0] * mt.col
  if index[0] >= mt.row or index[1] >= mt.col or num >= mt.row*mt.col:
    let msg = "matrix:[" & $mt.row & "," & $mt.col & "]  row:" & $index[0] & "  col:" & $index[1] & "  num:" & $num
    raise newException(MatrixException, "index out of bounds @getIndexNumber\n" & msg)
  return num

################ accessor ################
method `[]`*(mt: Matrix, index: array[2, int]): float {.base.} =
  let num = mt.getIndexNumber(index)
  return mt.val[num]

method `[]`*(mt: Matrix, row, col: int): float {.base.} =
  return mt[[row, col]]

method `[]`*(mt: Matrix, col: int): float {.base.} =
  if mt.row != 1:
    let msg = "matrix:[" & $mt.row & "," & $mt.col & "]  col:" & $col
    raise newException(MatrixException, "can not access as vector @[]\n" & msg)
  return mt[[0, col]]

method `[]=`*(mt: var Matrix, index: array[2, int], val: float) {.base.} =
  let num = mt.getIndexNumber(index)
  mt.val[num] = val
  
method `[]=`*(mt: var Matrix, row, col: int, val: float) {.base.} =
  mt[[row, col]] = val

method `$`*(mt: Matrix): string {.base.} =
  result &= "["
  for itr_r in 0..<mt.row:
    result &= "["
    for itr_c in 0..<mt.col:
      result &= ($mt[[itr_r, itr_c]])
      result &= (if itr_c != mt.col-1: " ," else: "")
    result &= "]"
    result &= (if itr_r != mt.row-1: "," else: "")
  result &= "]"

################ initialization ################
proc initMatrix*(row, col: int): Matrix =
  var val: seq[float]
  val.newSeq(row*col)
  var m = Matrix(val:val, row:row, col:col)
  return m
proc initMatrix*(shapes: array[2, int]): Matrix =
  return initMatrix(shapes[0], shapes[1])
proc initMatrix*(arr: seq[seq[float | int]]): Matrix =
  let row = arr.len
  let col = arr[0].len
  var m = initMatrix(row, col)
  for itr_r in 0..<row:
    for itr_c in 0..<col:
      m[[itr_r, itr_c]] = float(arr[itr_r][itr_c])
  return m
proc initMatrix*[R, C: static[int]](arr: array[R, array[C, float | int]]): Matrix =
  var arr2: seq[seq[float]]
  for itr_r in 0..<R:
    arr2.add(@[])
    for itr_c in 0..<C:
      arr2[itr_r].add(float(arr[itr_r][itr_c]))
  return initMatrix(arr2)
proc initMatrix*(arr: seq[float | int]): Matrix =
  return initMatrix(@[arr])
proc initMatrix*[C: static[int]](arr: array[C, float | int]): Matrix =
  var tmp: seq[float]
  for itr_c in 0..<C:
    tmp.add(float(arr[itr_c]))
  return initMatrix(@[tmp])

################# processing ################
method sum*(mt: Matrix): float {.base.} =
  for itr_r in 0..<mt.row:
    for itr_c in 0..<mt.col:
      result += mt[[itr_r, itr_c]]

method average*(mt: Matrix): float {.base.} =
  return mt.sum()/float(mt.row*mt.col)

method T*(mt: Matrix): Matrix {.base.} =
  result = initMatrix(mt.col, mt.row)
  for itr_r in 0..<mt.row:
    for itr_c in 0..<mt.col:
      result[[itr_c, itr_r]] = mt[[itr_r, itr_c]]

method asSeq*(mt: Matrix): seq[float] | seq[seq[float]] {.base.} =
  if mt.row == 1:
    return @[mt.val]
  else:
    var res: seq[seq[float]]
    for itr_r in 0..<mt.row:
      res.add(@[])
      for itr_c in 0..<mt.col:
        res[itr_r].add(mt[[itr_r, itr_c]])
    return res

method copy*(mt: Matrix): Matrix {.base.} =
  result = initMatrix(mt.row, mt.col)
  for itr_r in 0..<mt.row:
    for itr_c in 0..<mt.col:
      result[[itr_r, itr_c]] = mt[[itr_r, itr_c]]

proc map*(mt1: Matrix, mt2: Matrix, procedure: proc(a,b: float): float): Matrix =
  if mt1.row != mt2.row or mt1.col != mt2.col:
    let msg = "mt1:(" & $mt1.row & "," & $mt1.col & ")  mt2:(" & $mt2.row & "," & $mt2.col & ")"
    raise newException(MatrixException, "invalid map operation @map\n" & msg)
  result = initMatrix(mt1.row, mt1.col)
  for itr_r in 0..<mt1.row:
    for itr_c in 0..<mt1.col:
      result[[itr_r, itr_c]] = procedure(mt1[[itr_r, itr_c]], mt2[[itr_r, itr_c]])
  return result

method fill(mt: Matrix, scl: float): Matrix =
  result = initMatrix(mt.row, mt.col)
  for itr_r in 0..<mt.row:
    for itr_c in 0..<mt.col:
      result[[itr_r, itr_c]] = scl  

proc reshape*(arr: seq[float], row, col: int): Matrix =
  if row*col != len(arr):
    let msg = fmt"row:{row}, col:{col}, arrayLength:{arr.len}"
    raise newException(MatrixException, "invalid length @reshape\n" & msg)
  result = initMatrix(row, col)
  result.val = arr

proc reshape*(mt: Matrix, row, col: int): Matrix =
  return reshape(mt.val, row, col)

################ basis ################
method len*(mt: Matrix): int =
  return len(mt.val)

method shapes*(mt: Matrix): array[2, int] =
  return [mt.row, mt.col]

iterator items*(mt: Matrix): float =
  for i in 0..<len(mt):
    yield mt.val[i]

iterator rows*(mt: Matrix): seq[float] =
  for i in 0..<mt.row:
    yield mt.val[i*mt.row..<(i+1)*mt.row]

iterator cols*(mt: Matrix): seq[float] =
  let mtT = mt.T
  for i in 0..<mtT.row:
    yield mt.val[i*mtT.row..<(i+1)*mtT.row]

################ operator ################
method `==`*(mt1, mt2: Matrix): bool {.base.} =
  if mt1.row != mt2.row or mt1.col != mt2.col:
    return false
  for itr_r in 0..<mt1.row:
    for itr_c in 0..<mt1.col:
      if mt1[[itr_r, itr_c]] != mt2[[itr_r, itr_c]]:
        return false
  return true

method `!=`*(mt1, mt2: Matrix): bool {.base.} =
  return not (mt1 == mt2)

method `+`*(mt1, mt2: Matrix): Matrix {.base.} =
  if mt1.row != mt2.row or mt1.col != mt2.col:
    let msg = "mt1:(" & $mt1.row & "," & $mt1.col & ")  mt2:(" & $mt2.row & "," & $mt2.col & ")"
    raise newException(MatrixException, "invalid + operation @+\n" & msg)
  result = initMatrix(mt1.shapes)
  for itr_r in 0..<result.row:
    for itr_c in 0..<result.col:
      result[[itr_r, itr_c]] = mt1[[itr_r, itr_c]] + mt2[[itr_r, itr_c]]

method `+`*(mt: Matrix, scl: float): Matrix =
  if mt.row != 1 and mt.col != 1:
    let msg = "mt:(" & $mt.row & "," & $mt.col & ")  scalar:" & $scl
    raise newException(MatrixException, "invalid + operation @+\n" & msg)
  result = mt.copy()
  for itr_r in 0..<result.row:
    for itr_c in 0..<result.col:
      result[[itr_r, itr_c]] = result[[itr_r, itr_c]] + scl
  if mt.row != 1:
    result = result.T

proc `+`*(scl: float, mt: Matrix): Matrix =
  return mt + scl

method `-`*(mt1, mt2: Matrix): Matrix {.base.} =
  if mt1.row != mt2.row or mt1.col != mt2.col:
    let msg = "mt1:(" & $mt1.row & "," & $mt1.col & ")  mt2:(" & $mt2.row & "," & $mt2.col & ")"
    raise newException(MatrixException, "invalid - operation @-\n" & msg)
  result = initMatrix(mt1.shapes)
  for itr_r in 0..<result.row:
    for itr_c in 0..<result.col:
      result[[itr_r, itr_c]] = mt1[[itr_r, itr_c]] - mt2[[itr_r, itr_c]]

method `-`*(mt: Matrix, scl: float): Matrix =
  if mt.row != 1 and mt.col != 1:
    let msg = "mt:(" & $mt.row & "," & $mt.col & ")  scalar:" & $scl
    raise newException(MatrixException, "invalid - operation @-\n" & msg)
  result = mt.copy()
  for itr_r in 0..<result.row:
    for itr_c in 0..<result.col:
      result[[itr_r, itr_c]] = result[[itr_r, itr_c]] - scl
  if mt.row != 1:
    result = result.T

proc `-`*(scl: float, mt: Matrix): Matrix =
  var mt_scl = initMatrix(mt.shapes).fill(scl)
  return mt_scl - mt

method `*`*(mt1, mt2: Matrix): Matrix {.base.} =
  if mt1.col != mt2.row:
    let msg = "mt1:(" & $mt1.row & "," & $mt1.col & ")  mt2:(" & $mt2.row & "," & $mt2.col & ")"
    raise newException(MatrixException, "invalid * operation @*\n" & msg)
  let row = mt1.row
  let col = mt2.col
  result = initMatrix(row, col)
  for itr_r in 0..<row:
    for itr_c in 0..<col:
      var elem = 0.0
      for i in 0..<mt1.col:
        elem += mt1[[itr_r, i]] * mt2[[i, itr_c]]
      result[[itr_r, itr_c]] = elem

proc `*`*(coef: float, mt: Matrix): Matrix =
  result = initMatrix(mt.shapes)
  for itr_r in 0..<mt.row:
    for itr_c in 0..<mt.col:
      result[[itr_r, itr_c]] = coef * mt[[itr_r, itr_c]]

method `/`*(mt1, mt2: Matrix): Matrix {.base.} =
  if mt1.row != mt2.row or mt1.col != mt2.col:
    let msg = "mt1:(" & $mt1.row & "," & $mt1.col & ")  mt2:(" & $mt2.row & "," & $mt2.col & ")"
    raise newException(MatrixException, "invalid / operation @/\n" & msg)
  let row = mt1.row
  let col = mt2.col
  result = initMatrix(row, col)
  for itr_r in 0..<row:
    for itr_c in 0..<col:
      result[[itr_r, itr_c]] = mt1[[itr_r, itr_c]] / mt2[[itr_r, itr_c]]

method `/`*(mt: Matrix, scl: float): Matrix =
  result = mt.copy()
  for itr_r in 0..<result.row:
    for itr_c in 0..<result.col:
      result[[itr_r, itr_c]] = result[[itr_r, itr_c]] / scl

proc `/`*(scl: float, mt: Matrix): Matrix =
  var mt_scl = initMatrix(mt.shapes).fill(scl)
  return mt_scl / mt

################ matrix operation ################
proc identity*(dim: int): Matrix =
  result = initMatrix(dim, dim)
  for itr_r in 0..<dim:
    for itr_c in 0..<dim:
      result[[itr_c, itr_r]] = if itr_r == itr_c: 1.0 else: 0.0

method det*(mt: Matrix): float {.base.} =
  if mt.row != mt.col:
    let msg = "mt:(" & $mt.row & "," & $mt.col & ")"
    raise newException(MatrixException, "invalid matrix (not square matrix) @det\n" & msg)
  result = 1.0
  let n = mt.row
  var tmp = mt.copy()
  var buf: float = 0
  for itr_r in 0..<n:
    for itr_c in 0..<n:
      if itr_r < itr_c:
        buf = tmp[[itr_c, itr_r]]/tmp[[itr_r, itr_r]]
        for k in 0..<n:
          tmp[[itr_c, k]] = tmp[[itr_c, k]] - tmp[[itr_r, k]] * buf
  for i in 0..<n:
    result *= tmp[[i,i]]

method inv*(mt: Matrix): Matrix {.base.} =
  if mt.row != mt.col:
    let msg = "mt:(" & $mt.row & "," & $mt.col & ")"
    raise newException(MatrixException, "invalid matrix (not square matrix) @inv\n" & msg)
  # 吐き出し法
  let n = mt.row
  var tmp = mt.copy()
  var buf: float = 0
  result = identity(n)
  for itr_r in 0..<n:
    buf = 1.0/tmp[[itr_r, itr_r]]
    for itr_c in 0..<n:
      tmp[[itr_r, itr_c]] = tmp[[itr_r, itr_c]] * buf
      result[[itr_r, itr_c]] = result[[itr_r, itr_c]] * buf
    for itr_c in 0..<n:
      if itr_r != itr_c:
        buf = tmp[[itr_c, itr_r]]
        for k in 0..<n:
          tmp[[itr_c, k]] = tmp[[itr_c, k]] - tmp[[itr_r, k]] * buf
          result[[itr_c, k]] = result[[itr_c, k]] - result[[itr_r, k]] * buf

################ unversal function ################
method `power`*(mt1: Matrix, mt2: Matrix): Matrix =
  if mt1.col != mt2.col or (mt2.row != 1 and mt1.row < mt2.row):
    let msg = "mt1:(" & $mt1.row & "," & $mt1.col & ")  mt2:(" & $mt2.row & "," & $mt2.col & ")"
    raise newException(MatrixException, "invalid `power` operation @power\n" & msg)
  var mt2_new = mt2.copy()
  if mt2.row == 1:
    mt2_new = initMatrix(lc[mt2.val | (i <- 0..<mt1.row), seq[float]])
  result = map(mt1, mt2_new, pow)

method `power`*(mt: Matrix, scl: float): Matrix =
  let mt2 = initMatrix(mt.shapes).fill(scl)
  return power(mt, mt2)

################ TEST ################
import "./phaseTimer"
proc test_main(pt: var PhaseTimer) =
  pt.phase("plus ope"):
    var m1 = initMatrix([[1,2,3],[4,5,6]])
    echo(m1)
    echo(m1.T)
    echo(m1.row, "  ", m1.col)
    echo(m1[0,1])
    var m2 = initMatrix(@[@[10,20,30],@[40,50,60]])
    echo(m1 + m2)
    echo(m2 - m1)
  pt.phase("minus ope"):
    var m1 = initMatrix([1,2,3,4,5])
    var m2 = initMatrix([10,20,30,40,50])
    echo(1 + m1)
    echo(m1 + 1)
    echo(m1 + m2)
    echo(m2 - m1)
  pt.phase("mul ope"):
    var m1 = initMatrix([[1,-1],[-2,3]])
    var m2 = initMatrix([[1,2],[3,4]])
    echo(m1 * m2)
  pt.phase("dev ope"):
    var m1 = initMatrix([[1,2,3,4],[5,6,7,8]])
    var m2 = initMatrix([[2,4,6,8],[10,12,14,16]])
    echo(m2/m1)
    echo(m1/2.0)
  pt.phase("processing"):
    var m1 = initMatrix([[1,2,0,-1],[-1,1,2,0],[2,0,1,1],[1,-2,-1,1]])
    echo(m1.inv())
    var m2 = initMatrix([[2,-2,4,2],[2,-1,6,3],[3,-2,12,12],[-1,3,-4,4]])
    echo(det(m2))
  pt.phase("func"):
    var mt1 = initMatrix([[1,2,3],[4,5,6]])
    echo(power(mt1, initMatrix([1,2,3])))
    echo(power(mt1, 3))
  pt.phase("multi operator"):
    let N = 4
    let shift = initMatrix(lc[float(i) | (i <- 0..N), float])
    let nu = 4.0
    let x = 1.0
    let y = 1.0+(power(x-shift, 2)/nu)
    echo(y)
    var phi = power(y, -0.5*(nu+1.0))
    echo(phi)


import "./utils"
proc phi_t(x, nu: float, N: int): Matrix =
  let s = 1
  let shift = initMatrix(lc[float(i) | (i <- 0..<N), float])
  return power(1.0+power(x-shift, 2)/nu, -0.5*(nu*1.0))
proc baysian_test(pt: var PhaseTimer) =
  let N = 64
  let M = 128
  let alpha = 1.0
  let beta = 16.0
  let NU = 4.0
  var signal: seq[float]
  var line: seq[float]
  for i in 0..<N:
    let START = i
    let END = START + M
    let ohlc = getHistricalData(r"./../../resources/DAT_ASCII_EURUSD_M1_2007.csv", ';', START, END)
    let close = initMatrix(ohlc[4])
    let t = close - close.average()
    let xlist = lc[float(i) | (i <- 0..<M), float]
    let phi = initMatrix(lc[phi_t(x, NU, M).asSeq() | (x <- xlist), seq[float]])
    let sigma_N = (alpha * identity(phi.shapes[1]) + beta * (phi.T * phi)).inv()
    let mu_N = beta * (sigma_N * (phi.T * t.T))
    #let y = initMatrix(lc[(mu_N * phi_t(x, NU, M)).asSeq() | (x <- xlist), seq[float]])
    #echo("y:", y)
    signal.add(t[len(t)-1])
    line.add(mu_N.T[len(mu_N.T)-1])
  echo(signal)
  echo(line)


if isMainModule:
  var pt = initPhaseTimer()
  pt.phase("test_main"):
    test_main(pt)
  pt.phase("baysian"):
    baysian_test(pt)