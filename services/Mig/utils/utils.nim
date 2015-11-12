import strutils, times

proc `??`*[T] (first, second: T): T {.noSideEffect.} =
    if first == nil: second else: first

proc eqIgnoreCase*(a, b: string): bool {.noSideEffect.} =
    cmpIgnoreCase(a, b) == 0

proc trimStart*(value: string, c: char): string {.noSideEffect.} =
    value.strip(true, false, {c})

proc toRfcDate*(time: Time): string =
    time.getGMTime().format("ddd, dd MMM yyyy HH:mm:ss") & " GMT"

when isMainModule:
    assert "123" == (string(nil) ?? "123")
    assert "123" == ("123" ?? "234")

    assert eqIgnoreCase("abc", "aBc")
    assert eqIgnoreCase("abc", "ABC")
    assert (not eqIgnoreCase("abc", "cba"))

    assert "qwer" == trimStart("qwer", ' ')
    assert "qwerAAA" == trimStart("AAAqwerAAA", 'A')

    assert "Tue, 19 Jan 2038 03:14:07 GMT" == fromSeconds(2147483647).toRfcDate()

    echo "[utils] OK: compiled ", CompileDate, " ", CompileTime
