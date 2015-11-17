import json, marshal, strutils, sequtils, times
import utils/utils, utils/crypt, utils/dbstorage, utils/rsa, utils/sha3h, state

type
    Field = object
        name: string
        title: string
        maxlen: int
        pattern: string
        value: string
        rows: int
        ro: bool

    Form = object of RootObj
        fields: seq[Field]
        prev, next: bool
        state: string

const MinPage = 1
const MaxPage = 5

# Code HELL =/

proc f1(state: State): string =
    let user = state.user
    $$(Form(fields: @[
        Field(name: "name", title: "Your name", maxlen: 32, value: user.name),
        Field(name: "sname", title: "Your surname", maxlen: 32, value: user.sname),
        Field(name: "bdate", title: "Date of birth", maxlen: 16, value: user.bdate),
        Field(name: "bplace", title: "Place of birth", maxlen: 48, value: user.bplace),
        Field(name: "mphone", title: "Your Mind`iPhone number", maxlen: 16, value: user.phone),
    ], prev: false, next: true, state: encrypt($state)))

proc f2(state: State): string =
    let user = state.user
    $$(Form(fields: @[
        Field(name: "occup", title: "Current occupation", maxlen: 32, value: user.occup),
        Field(name: "empl", title: "Employer", maxlen: 48, value: user.empl),
    ], prev: true, next: true, state: encrypt($state)))

proc f3(state: State): string =
    let user = state.user
    $$(Form(fields: @[
        Field(name: "thought", title: "Some thought from your mind", maxlen: 32, value: user.thought, pattern: "\\w{16,}"),
        Field(name: "sign", title: "Signature", maxlen: 1024, value: "", pattern: "[0-9a-fA-F]+", rows: 8)
    ], prev: true, next: true, state: encrypt($state)))

proc f4(state: State): string =
    let citizens = "Last citizens joined:\n" & (try: join(getLastJoins().map(proc(ctz: JoinInfo): string =
        "$#: $# $#\n   from $#\n   thinks that $#" % [ctz.join.toShortTime(), ctz.name, ctz.sname, ctz.occup, ctz.thought]
    ), "\n") except: "error")
    $$(Form(fields: @[
        Field(title: "Last citizens", value: citizens, rows: 10, ro: true),
        Field(name: "public", title: "Type `yes` if you are public enough", maxlen: 3, value: ""),
        Field(name: "offer", title: "Type `yes`", maxlen: 3, value: "")
    ], prev: true, next: true, state: encrypt($state)))

proc f5(state: State): string =
    let text = if isNil(state): "Failed to find your data" else: ("\nname: $#\nsurname: $#\nbirth date: $#\nbirth place: $#\nphone: $#\noccupation: $#\nemployer: $#\nthought: $#" % [state.user.name, state.user.sname, state.user.bdate, state.user.bplace, state.user.phone, state.user.occup, state.user.empl, state.user.thought])
    $$(Form(fields: @[
        Field(value: "Congratulations!\n\nYou are citizen of Turio now!\n" & text, rows: 5, ro: true)
    ], prev: false, next: false, state: ""))

proc init(login: string): string =
    f1(newState(login))

proc form(page = 1, state: State): string =
    case page
    of 1: f1(state)
    of 2: f2(state)
    of 3: f3(state)
    of 4: f4(state)
    of 5: f5(state)
    else: f1(state)

proc val(json: JsonNode, name: string, maxlen: int = 64): string =
    let value = json[name].getStr()
    if isNilOrEmpty(value) or value.len > maxlen: nil else: value

proc validateF1(data: tuple[name, sname, bdate, bplace, mphone: string]): string =
    if isNil(data.name): return "Check your name"
    if isNil(data.sname): return "Check your surname"
    if isNil(data.bdate): return "Check your birth date"
    if isNil(data.bplace): return "Check your birth place"
    if isNil(data.mphone): return "Check your Mind`iPhone"

proc validateF2(data: tuple[occup, empl: string]): string =
    if isNil(data.occup): return "Check your current occupation"
    if isNil(data.empl): return "Check your employer"

proc validateF3(data: tuple[thought, sign: string]): string =
    if isNil(data.thought) or data.thought.len < 16: return "Check your mind!"
    if isNil(data.sign) or (not checkSign(data.thought.trimEnd('='), data.sign)) or (not isUnique(data.thought)): return "Not trusted!"

proc validateF4(data: tuple[offer, public: string]): string =
    if not eqIgnoreCase(data.offer, "yes"): return "You must agree with offer"

proc saveF1(data: tuple[name, sname, bdate, bplace, mphone: string], state: State) =
    state.user.name = data.name
    state.user.sname = data.sname
    state.user.bdate = data.bdate
    state.user.bplace = data.bplace
    state.user.phone = data.mphone

proc saveF2(data: tuple[occup, empl: string], state: State) =
    state.user.occup = data.occup
    state.user.empl = data.empl

proc saveF3(data: tuple[thought, sign: string], state: State) =
    state.user.thought = data.thought

proc saveF4(data: tuple[offer, public: string], state: State) =
    state.public = eqIgnoreCase(data.public, "yes")
    state.offer = true
    state.join = getTime()
    discard tryAdd(state)
    discard tryAdd(newJoinInfo(state))

proc update(json: JsonNode, state: State, check: bool): string =
    if isNil(json) or json.kind != JObject:
        return "Invalid request"
    case state.page
    of 1:
        let data = (name: json.val("name", 32), sname: json.val("sname", 32), bdate: json.val("bdate", 16), bplace: json.val("bplace", 48), mphone: json.val("mphone", 16))
        let error = if check: validateF1(data) else: nil
        if isNil(error):
            saveF1(data, state)
        error
    of 2:
        let data = (occup: json.val("occup", 32), empl: json.val("empl", 48))
        let error = if check: validateF2(data) else: nil
        if isNil(error):
            saveF2(data, state)
        error
    of 3:
        let data = (thought: json.val("thought", 32), sign: json.val("sign", 1024))
        let error = if check: validateF3(data) else: nil
        if isNil(error):
            saveF3(data, state)
        error
    of 4:
        let data = (offer: json.val("offer", 3), public: json.val("public", 3))
        let error = if check: validateF4(data) else: nil
        if isNil(error):
            saveF4(data, state)
        error
    else: nil

proc nextForm*(login: string, json: JsonNode): tuple[form, error: string] =
    let data = findDataInfo(login)
    if not isNil(data):
        return (form: f5(data), error: string(nil))

    let stateVal = json["state"].getStr()
    if isNilOrEmpty(stateVal):
        return (form: init(login), error: string(nil))

    let state = tryParseState(decrypt(stateVal))
    if isNil(state) or state.login != login:
        return (form: init(login), error: string(nil))

    let fields = json["fields"]
    let action = json["action"].getStr()

    var next = false

    case action
    of "save": return (form: update(fields, state, false), error: string(nil))
    of "load": return (form: form(state.page, state), error: string(nil))
    of "next": next = true
    of "prev": discard
    else: return (form: string(nil), error: "Unknown action")

    let error = update(fields, state, next)
    if not isNil(error):
        return (form: string(nil), error: error)

    state.page += (if next: 1 else: -1)
    if state.page < MinPage or state.page > MaxPage:
        state.page = 1
    (form: form(state.page, state), error: string(nil))
