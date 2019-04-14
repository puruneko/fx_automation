import times
import tables
import strutils
import strformat
import macros

type
  PhaseTimer* = object
    time: Table[string, float]
    level: int
    inPostfix: string
    outPostfix: string
    levelIncreament: int

proc initPhaseTimer*(inPostfix: string = "start.", outPostfix: string = "end.", levelIncreament: int = 2): PhaseTImer =
  result.time = initTable[string, float]()
  result.level = 0
  result.inPostfix = inPostfix
  result.outPostfix = outPostfix
  result.levelIncreament = levelIncreament

method enterProcess(pt: var PhaseTimer, label: string) {.base.} =
  pt.time[label] = cpuTime()
  pt.level += pt.levelIncreament

method leaveProcess(pt: var PhaseTimer, label: string) {.base.} =
  pt.time.del(label)
  pt.level -= pt.levelIncreament

method progressTime*(pt: PhaseTimer, label: string): float {.base.} =
  return cpuTime() - pt.time[label]

method enter*(pt: var PhaseTimer, msg: string) {.base.} =
  pt.enterProcess(msg)
  let bar = "-".repeat(pt.level)
  echo(fmt"{bar}> {msg} {pt.inPostfix}")

method leave*(pt: var PhaseTimer, msg: string) {.base.} =
  let bar = "-".repeat(pt.level)
  let progressTime = pt.progressTime(msg)
  echo(fmt"<{bar} {msg} {pt.outPostfix}({progressTime:1.3f}[s])")
  pt.leaveProcess(msg)

method msg*(pt: PhaseTimer, msg: string, disp: string, displayTime: bool = false) {.base.} =
  let bar = "-".repeat(pt.level)
  let progressTime: string = if displayTime: $(pt.progressTime(msg)) else: ""
  echo(fmt"{bar}| {disp} {pt.outPostfix}({progressTime:1.3f}[s])")

method getLevel*(pt: PhaseTimer): int {.base.} =
  return pt.level

template phase*(pt: var PhaseTimer, label: string, body: untyped) =
  block:
    pt.enter(label)
    body
    pt.leave(label)


if isMainModule:
  var pt = initPhaseTimer()
  pt.phase("test"):
    var i = 1
    echo("In phase block")
    echo(i)
  pt.phase("sample"):
    var i = 10
    echo("In phase block")
    echo(i)
