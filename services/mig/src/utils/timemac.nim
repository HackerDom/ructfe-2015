import times
import utils, sha3h, crypt

proc mac(val: string, sec: int): string =
    sha3(Key & $sec & (val ?? "")).substr(0, 11).hex()

proc mac*(val: string): string =
    mac(val, getTime().sec())

proc checkMac*(val, mac: string, ttl: int): bool =
    let now = getTime().sec()
    for sec in now - ttl + 1..now:
        if mac(val, sec) == mac:
            return true
    return false

when isMainModule:
    import os

    assert checkMac(nil, mac(nil), 1)
    assert checkMac("", mac(""), 1)
    assert checkMac("123", mac("123"), 1)

    let val = mac("123")
    sleep(2000)
    assert checkMac("123", val, 3)
    assert(not checkMac("123", val, 1))

    echo "[timemac] OK: compiled ", CompileDate, " ", CompileTime
