import redis, times, sequtils
import utils, ../state

var db: ref Redis = new Redis
db[] = open()

const AuthKeyPrefix = "auth:"
const JoinKeyPrefix = "info:"
const DataKeyPrefix = "data:"
const ThghKeyPrefix = "thgh:"

# Single thread!
proc reconnect(): bool =
    try:
        try: db[].quit() except: discard
        db[] = open()
        return true
    except: discard

template withReconnect(command: expr): expr =
    for i in 0..1:
        try:
            command
        except:
            if reconnect(): discard
            else: raise

proc tryAdd(db: Redis, key, value: string): bool {.gcsafe.} =
    db.setNX(key, value)

proc find(db: Redis, key: string): string {.gcsafe.} =
    let value = db.get(key)
    if value == redisNil: nil else: value

proc addOrGet(db: Redis, key, value: string): string {.gcsafe.} =
    if tryAdd(db, key, value): value else: find(db, key)

proc tryAdd(key, value: string): bool =
    withReconnect: return db[].tryAdd(key, value)

proc find(key: string): string =
    withReconnect: return db[].find(key)

proc addOrGet(key, value: string): string =
    withReconnect: return db[].addOrGet(key, value)

proc zadd(key, value: string): bool =
    withReconnect: return db[].zadd(key, getTime().sec(), value) == 1

proc getLast(key: string, minutes: int = 15): seq[string] =
    withReconnect: return db[].zrevrangebyscore(key, "+inf", $getTime().addMinutes(-minutes).sec())

proc isUniqueThought*(key: string): bool =
    tryAdd(ThghKeyPrefix & key, "")

### AuthInfo ###
proc addOrGetAuth*(auth: tuple[login, pass: string]): string =
    addOrGet(AuthKeyPrefix & auth.login, auth.pass)

### JoinInfo ###
proc tryAdd*(info: JoinInfo): bool =
    zadd(JoinKeyPrefix, $info)

proc getLastJoins*(): seq[JoinInfo] =
    getLast(JoinKeyPrefix).map(proc(val: string): JoinInfo = tryParseJoinInfo(val))

### DataInfo ###
proc tryAdd*(data: State): bool =
    tryAdd(DataKeyPrefix & data.login, $data)

proc findDataInfo*(login: string): State =
    let data = find(DataKeyPrefix & login)
    if isNil(data): nil else: tryParseState(data)

when isMainModule:
    import threadpool, base64
    import crypt

    let key = "qwer:" & encode(rnd(32))

    assert isNil(find(key))
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
        let key = "key:" & encode(rnd(32))
        let val1 = "val:" & encode(rnd(32))
        let val2 = "val:" & encode(rnd(32))

        k[i] = key
        v1[i] = val1
        v2[i] = val2

        a1[i] = spawn db[].tryAdd(key, val1)
        a2[i] = spawn db[].tryAdd(key, val2)

    for i in 0..Iterations:
        let i1 = ^a1[i]
        let i2 = ^a2[i]
        assert i1 xor i2
        let v = if i1: v1[i] else: v2[i]
        assert db[].find(k[i]) == v

    echo "[dbstorage] OK: compiled ", CompileDate, " ", CompileTime
