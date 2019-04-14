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
  InnerContents* = object
    a1*: int
    a2*: int
  Contents* = object
    f1*: InnerCOntents
    f2*: InnerContents
  MyTable* = Table[string, Contents]

proc update(mt: var MyTable, id: string, f1: int, f2: int) =
  mt[id].f1.a1 = f1
  mt[id].f2.a1 = f2

proc main() =
  var mt: MyTable = initTable[string, Contents]()
  mt["a"] = Contents(f1: InnerContents(a1: 0, a2: 0), f2: InnerContents(a1: 0, a2: 0))
  update(mt, "a", 1, 2)
  echo(mt)

if isMainModule:
  main()