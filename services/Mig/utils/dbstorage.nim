import redis

let db {.global.} = open()

proc tryAdd(db: Redis, key, value: string): bool {.gcsafe.} =
    db.setNX(key, value)

proc find(db: Redis, key: string): string {.gcsafe.} =
    let value = db.get(key)
    if value == redisNil: nil else: value

proc tryAdd*(key, value: string): bool =
    db.tryAdd(key, value)

proc find*(key: string): string =
    db.find(key)

when isMainModule:
    import threadpool, base64
    import crypt

    let key = "qwer:" & encode(randomStr(32))

    assert find(key) == nil
    assert tryAdd(key, "1234")
    assert (not tryAdd(key, "5678"))
    assert find(key) == "1234"

    const Iterations = 100

    var a1: array[0..Iterations, FlowVar[bool]]
    var a2: array[0..Iterations, FlowVar[bool]]

    var k: array[0..Iterations, string]
    var v1: array[0..Iterations, string]
    var v2: array[0..Iterations, string]

    for i in 0..Iterations:
        let key = "key:" & encode(randomStr(32))
        let val1 = "val:" & encode(randomStr(32))
        let val2 = "val:" & encode(randomStr(32))

        k[i] = key
        v1[i] = val1
        v2[i] = val2

        a1[i] = spawn db.tryAdd(key, val1)
        a2[i] = spawn db.tryAdd(key, val2)

    for i in 0..Iterations:
        let i1 = ^a1[i]
        let i2 = ^a2[i]
        assert i1 xor i2
        let v = if i1: v1[i] else: v2[i]
        assert db.find(k[i]) == v

    echo "[dbstorage] OK: compiled ", CompileDate, " ", CompileTime
