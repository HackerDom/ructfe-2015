import strutils, times

proc `??`*[T](first, second: T): T {.noSideEffect.} =
    if isNil(first): second else: first

template `?.`*(first, second: expr): expr =
    if isNil(first): nil else: first.second

proc isNilOrEmpty*(value: string): bool {.noSideEffect.} =
    isNil(value) or value == ""

proc eqIgnoreCase*(a, b: string): bool {.noSideEffect.} =
    cmpIgnoreCase(a, b) == 0

proc trimStart*(value: string, c: char): string {.noSideEffect.} =
    value.strip(true, false, {c})

proc trimEnd*(value: string, c: char): string {.noSideEffect.} =
    value.strip(false, true, {c})

proc splitKeyValue*(s: string, delim: char): tuple[key, val: string] {.noSideEffect.} =
    let idx = s.find(delim)
    if idx < 0:
        return (s, string(nil))
    (key: s.substr(0, idx - 1), val: s.substr(idx + 1))

proc isHex*(value: string): bool {.noSideEffect.} =
    for i in 0..value.len - 1:
        if not (value[i] in HexDigits):
            return false
    true

proc `xor`*(s1, s2: string): string {.noSideEffect.} =
    if s1.len != s2.len:
        raise
    result = newString(s1.len)
    for i in 0..s1.len - 1:
      result[i] = chr(ord(s1[i]) xor ord(s2[i]))

const Digits = "0123456789abcdef"
proc hex*(data: string): string {.noSideEffect.} =
    result = newString(data.len shl 1)
    for i in 0..data.len - 1:
        let b = ord(data[i])
        result[i shl 1] = Digits[b shr 4]
        result[(i shl 1) + 1] = Digits[b and 0xf]

proc intToBStr*(val: int): string =
    result = newString(4)
    for i in 0..3:
        result[i] = chr((val shr (i shl 3)) and 0xff);

proc toRfcDate*(time: Time): string =
    time.getGMTime().format("ddd, dd MMM yyyy HH:mm:ss") & " GMT"

proc toShortTime*(time: Time): string =
    time.getGMTime().format("HH:mm:ss")

proc addMinutes*(time: Time, m: int): Time {.noSideEffect.} =
    fromSeconds(time.toSeconds() + m.toFloat() * 60.0)

proc sec*(time: Time): int =
    time.toSeconds().toInt()

when isMainModule:
    assert "123" == (string(nil) ?? "123")
    assert "123" == ("123" ?? "234")

    assert eqIgnoreCase("abc", "aBc")
    assert eqIgnoreCase("abc", "ABC")
    assert (not eqIgnoreCase("abc", "cba"))

    assert "qwer" == trimStart("qwer", ' ')
    assert "qwerAAA" == trimStart("AAAqwerAAA", 'A')

    assert(("", string(nil)) == splitKeyValue("", ':'))
    assert(("abc", string(nil)) == splitKeyValue("abc", ':'))
    assert(("abc", "") == splitKeyValue("abc:", ':'))
    assert(("", "abc") == splitKeyValue(":abc", ':'))
    assert(("a", "bc") == splitKeyValue("a:bc", ':'))

    assert isHex("")
    assert isHex("0123456789abcdef")
    assert isHex("0123456789ABCDEF")
    assert(not(isHex("qwer")))

    assert "" == ("" xor "")
    assert "\x00\x00\x00" == ("\x00\x7f\xff" xor "\x00\x7f\xff")
    assert "\xff\xff\xff" == ("\x00\xf0\xff" xor "\xff\x0f\x00")

    assert "" == hex("")
    assert "00" == hex("\0")
    assert "20" == hex(" ")
    assert "3132333435" == hex("12345")

    assert "Tue, 19 Jan 2038 03:14:07 GMT" == fromSeconds(2147483647).toRfcDate()

    echo "[utils] OK: compiled ", CompileDate, " ", CompileTime
