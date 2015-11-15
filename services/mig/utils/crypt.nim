import os, strutils, sequtils, random, nimAES, base64

#type TLock = ref object
#var lock {.global.} = new TLock

proc randomStr*(len: Natural): string =
    let buf = random.urandom(len)
    assert len == buf.len
    join(buf.map(proc(b: uint8): string = $chr(b)))

const IVLen = 16
const KeyLen = 32

proc genIV(): string =
    randomStr(IVLen)

proc genOrReadKey(): string =
    let appDir = getAppDir()
    let filepath = joinPath(appDir, "key")
    try:
        result = readFile(filepath)
        if result.len != KeyLen:
            raise
    except:
        result = randomStr(KeyLen)
        writeFile(filepath, result)

let key {.global.} = genOrReadKey()

const ZeroPad = '\0'
const OnePad = '\255'

proc pad(data: string): string =
    let padlen = 16 - (data.len and 15)
    repeat(ZeroPad, padlen - 1) & OnePad & data

proc unpad(data: string): string =
    data.substr(data.find(OnePad) + 1)

proc encrypt(key, data: string): string {.gcsafe.} =
    var aes = initAES()
    if not aes.setEncodeKey(key):
        raise
    let iv = genIV()
    encode(iv.substr() & aes.encryptCBC(iv, pad(data)), 0x7fffffff)

proc decrypt(key, data: string): string {.gcsafe.} =
    var aes = initAES()
    if not aes.setDecodeKey(key):
        raise
    let raw = decode(data)
    unpad(aes.decryptCBC(raw.substr(0, IVLen - 1), raw.substr(IVLen)))

proc encrypt*(data: string): string =
    encrypt(key, data)

proc decrypt*(data: string): string =
    decrypt(key, data)

when isMainModule:
    assert key.len == KeyLen
    assert genIV().len == IVLen
    assert genIV() != genIV()

    echo "    Key: ", encode(key)
    echo "     IV: ", encode(genIV())

    assert "" == unpad(pad(""))
    assert "qwer" == unpad(pad("qwer"))
    assert "0123456789ABCDEF" == unpad(pad("0123456789ABCDEF"))

    assert "" == decrypt(encrypt(""))
    assert "qwer" == decrypt(encrypt("qwer"))
    assert "0123456789ABCDEF" == decrypt(encrypt("0123456789ABCDEF"))

    import threadpool

    const Iterations = 100

    var a: array[0..Iterations, string]
    var b: array[0..Iterations, FlowVar[string]]

    for i in 0..Iterations:
        let plain = randomStr(32)
        a[i] = plain
        b[i] = spawn decrypt(key, encrypt(key, plain))

    for i in 0..Iterations:
        assert a[i] == (^b[i])

    echo "[crypt] OK: compiled ", CompileDate, " ", CompileTime
