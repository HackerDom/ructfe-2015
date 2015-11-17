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
        head: string
        fields: seq[Field]
        prev, next: bool
        proof: bool
        state: string

const MinPage = 1
const MaxPage = 5

# Code HELL =/

proc form1(state: State): string =
    let user = state.user
    $$(Form(head: "General information about yourself:", fields: @[
        Field(name: "name", title: "Your name", maxlen: 32, value: user.name),
        Field(name: "sname", title: "Your surname", maxlen: 32, value: user.sname),
        Field(name: "bdate", title: "Date of birth", maxlen: 16, value: user.bdate),
        Field(name: "bplace", title: "Place of birth", maxlen: 48, value: user.bplace),
        Field(name: "mphone", title: "Your mind`iPhone number", maxlen: 16, value: user.phone),
    ], prev: false, next: true, state: encrypt($state)))

proc form2(state: State): string =
    let user = state.user
    $$(Form(head: "Information about your previous location and employer:", fields: @[
        Field(name: "occup", title: "Current occupation", maxlen: 32, value: user.occup),
        Field(name: "empl", title: "Employer", maxlen: 48, value: user.empl),
    ], prev: true, next: true, state: encrypt($state)))

proc form3(state: State): string =
    let user = state.user
    $$(Form(head: "We need to check that your motives are pure and right from your heart. Generate unique thought from your mind. To verify that you think like us, we ask you to fill the mental sign field.", fields: @[
        Field(name: "thought", title: "Some thought from your mind", maxlen: 32, value: user.thought, pattern: "\\w{16,}"),
        Field(name: "sign", title: "Mental signature", maxlen: 1024, value: "", pattern: "[0-9a-fA-F]+", rows: 8)
    ], prev: true, next: true, state: encrypt($state)))

proc form4(state: State): string =
    let citizens = "Last citizens joined:\n" & (try: join(getLastJoins().map(proc(ctz: JoinInfo): string =
        "$#: $# $#\n   from $#\n   thinks that $#" % [ctz.join.toShortTime(), ctz.name ?? "", ctz.sname ?? "", ctz.occup ?? "", ctz.thought ?? ""]
    ), "\n") except: "error")
    $$(Form(head: "Under law T-31337 we must give you information about the latest joined citizens. Confirm our offer to join us.", fields: @[
        Field(title: "Last citizens", value: citizens, rows: 10, ro: true),
        Field(name: "public", title: "Type `yes` if you are public enough", maxlen: 3, value: ""),
        Field(name: "offer", title: "Type `yes` to offer", maxlen: 3, value: "")
    ], prev: true, next: true, state: encrypt($state)))

proc form5(state: State): string =
    let text =
        if isNil(state): "Failed to find your data"
        else: ("\nname: $#\nsurname: $#\nbirth date: $#\nbirth place: $#\nphone: $#\noccupation: $#\nemployer: $#\nthought: $#" % [state.user.name ?? "", state.user.sname ?? "", state.user.bdate ?? "", state.user.bplace ?? "", state.user.phone ?? "", state.user.occup ?? "", state.user.empl ?? "", state.user.thought ?? ""])
    $$(Form(fields: @[
        Field(value: "Congratulations!\n\nYou are citizen of Turio now!\n" & text, rows: 12, ro: true)
    ], prev: false, next: false, state: ""))

proc init(login: string): string =
    form1(newState(login))

proc form(page = 1, state: State): string =
    case page
    of 1: form1(state)
    of 2: form2(state)
    of 3: form3(state)
    of 4: form4(state)
    of 5: form5(state)
    else: form1(state)

proc val(json: JsonNode, name: string, maxlen: int = 64): string =
    let value = json[name].getStr()
    if isNilOrEmpty(value) or value.len > maxlen: nil else: value

proc checkForm1(data: tuple[name, sname, bdate, bplace, mphone: string]): string =
    if isNil(data.name): return "Check your name"
    if isNil(data.sname): return "Check your surname"
    if isNil(data.bdate): return "Check your birth date"
    if isNil(data.bplace): return "Check your birth place"
    if isNil(data.mphone): return "Check your mind`iPhone"

proc checkForm2(data: tuple[occup, empl: string]): string =
    if isNil(data.occup): return "Check your current occupation"
    if isNil(data.empl): return "Check your employer"

proc checkForm3(data: tuple[thought, sign: string]): string =
    if isNil(data.thought) or data.thought.len < 16: return "Check your mind!"
    if isNil(data.sign) or (not checkSign(data.thought.hex(), data.sign)) or (not isUniqueThought(data.thought)): return "Not trusted!"

#proc checkProof(proof: string): bool =
#    if isNil(proof): false
#    else: ord(proof[0]) == 0x77 and ord(proof[1]) == 0x77 and (ord(proof[2]) shr 4) == 0x7 and isUniqueProof(proof)

proc checkForm4(data: tuple[offer, public, proof: string]): string =
    if not eqIgnoreCase(data.offer, "yes"): return "You must agree with offer"
#    if not checkProof(data.proof): return "Invalid proof of work"

proc saveForm1(data: tuple[name, sname, bdate, bplace, mphone: string], state: State) =
    state.user.name = data.name
    state.user.sname = data.sname
    state.user.bdate = data.bdate
    state.user.bplace = data.bplace
    state.user.phone = data.mphone

proc saveForm2(data: tuple[occup, empl: string], state: State) =
    state.user.occup = data.occup
    state.user.empl = data.empl

proc saveForm3(data: tuple[thought, sign: string], state: State) =
    state.user.thought = data.thought

proc saveForm4(data: tuple[offer, public, proof: string], state: State, next: bool) =
    state.public = eqIgnoreCase(data.public, "yes")
    if next:
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
        let error = if check: checkForm1(data) else: nil
        if isNil(error):
            saveForm1(data, state)
        return error
    of 2:
        let data = (occup: json.val("occup", 32), empl: json.val("empl", 48))
        let error = if check: checkForm2(data) else: nil
        if isNil(error):
            saveForm2(data, state)
        return error
    of 3:
        let data = (thought: json.val("thought", 32), sign: json.val("sign", 1024))
        let error = if check: checkForm3(data) else: nil
        if isNil(error):
            saveForm3(data, state)
        return error
    of 4:
        let data = (offer: json.val("offer", 3), public: json.val("public", 3), proof: json.val("proof"))
        let error = if check: checkForm4(data) else: nil
        if isNil(error):
            saveForm4(data, state, check)
        return error
    else: return nil

proc nextForm*(login: string, json: JsonNode): tuple[form, error: string] =
    let data = findDataInfo(login)
    if not isNil(data):
        return (form: form5(data), error: string(nil))

    let stateVal = json["state"].getStr()
    if isNilOrEmpty(stateVal):
        return (form: init(login), error: string(nil))

    let state = try: tryParseState(decrypt(stateVal)) except: nil
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

    return (form: form(state.page, state), error: string(nil))
