{.compile: "../lib/rhash/sha3.c"}

const sha3_256_hash_size = 32

{.push importc, cdecl.}

proc rhash_sha3(bits: int = sha3_256_hash_size * 8, data: cstring, size: int, res: array[sha3_256_hash_size, char])

{.pop.}

proc calc_sha3(data: cstring): array[sha3_256_hash_size, char] =
    rhash_sha3(sha3_256_hash_size * 8, data, data.len, result)

proc sha3*(data: string): string =
    result = newString(sha3_256_hash_size)
    let hash = calc_sha3(data)
    for i in 0 .. 31: result[i] = hash[i]

import strutils, utils

const opad = repeat('\x5c', sha3_256_hash_size)
const ipad = repeat('\x36', sha3_256_hash_size)

proc hmac_sha3*(key, data: string): string =
    let hkey =
        if key.len > sha3_256_hash_size:
            sha3(key)
        elif key.len < sha3_256_hash_size:
            key & repeat('\0', sha3_256_hash_size - key.len)
        else:
            key
    sha3((opad xor hkey) & sha3((ipad xor hkey) & data))

when isMainModule:
    assert sha3("").hex() == "a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a"
    assert sha3("abc").hex() == "3a985da74fe225b2045c172d6bd390bd855f086e3e9d525b46bfe24511431532"
    assert sha3("abcdefghbcdefghicdefghijdefghijkefghijklfghijklmghijklmnhijklmnoijklmnopjklmnopqklmnopqrlmnopqrsmnopqrstnopqrstu").hex() == "916f6061fe879741ca6469b43971dfdb28b1a32dc36cb3254e812be27aad1d18"

    import times

    const Iterations = 10000

    let start = cpuTime()
    for i in 0..Iterations:
        discard sha3("abc")
    echo "[sha3h] ", Iterations, " iterations: CPU time [s] - ", cpuTime() - start

    echo "[sha3h] OK: compiled ", CompileDate, " ", CompileTime
