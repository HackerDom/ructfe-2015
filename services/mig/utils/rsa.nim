import ../lib/bignum, ../lib/gmp
import utils

const B16 = 16

const PubExp = culong 65537
const Modulus = "00c6207dea1e8d97ebdb2c3d100b50a8de2659affb944bca1577345791904444b481bec47427486724393d7c2d52e631c26d8901b637081c1bdc3a398e924191ccf0b3d7c78dabe28b9ed49afa207bfcb4bfc1341b2e51a8d43bf2ff4e498c7e0484d630c8747be706a807f338a1a38463a5a88be69694230646018eed6ee7c32e8a24a425b4deb694e7434a73643477b21aabf9ef7d2beb90347ef844e0891bd466d456612478706938796f62811df6d986f3bcf4fcb795899ae5e40846fdea86e7010188c7d80157a0f306e5286df5b98af2bcf2562a3cde357824e4739da1b186316689d52186f7d9f109719c2317c85690b23d916a5b45890c4163324f8ef1"
#const PrivExp = ""

proc newIntOrZero(val: string, base: cint): Int =
    if val.isNilOrEmpty(): newInt(0) else: newInt(val, base)

#proc exp2(z, x, y, m: Int): Int =
#    mpz_powm_sec(z[], x[], y[], m[])
#    z

#proc exp2(x, y, m: Int): Int =
#    newInt().exp2(x, y, m)

proc enc(m: Int): Int =
    exp(m, PubExp, newInt(Modulus, B16))

#proc dec(c: Int): Int =
#    exp2(c, newInt(PrivExp, B16), newInt(Modulus, B16))

#proc sign*(hash: string): string =
#    `$`(dec(newIntOrZero(hash, B16)), B16)

proc checkSign*(hash, sign: string): bool =
    if not(sign.isHex() and hash.isHex()):
        return false
    enc(newIntOrZero(sign, B16)) == newIntOrZero(hash, B16)

#when isMainModule:
#    import utils, sha3h

#    let hash = sha3("ABC").hex()
#    assert checkSign("", sign(""))
#    assert checkSign("1", sign("1"))
#    assert checkSign(hash, sign(hash))

#    import times

#    const Iterations = 10000

#    let s = sign(hash)
#    let start = cpuTime()
#    for i in 0..Iterations:
#        assert checkSign(hash, s)
#    echo "[rsa] ", Iterations, " iterations: CPU time [s] - ", cpuTime() - start

#    echo "[rsa] OK: compiled ", CompileDate, " ", CompileTime
