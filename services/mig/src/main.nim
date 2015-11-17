import os, strutils, sequtils, asynchttpserver, asyncdispatch, asyncnet, strtabs, tables, times, mimetypes, json, cgi, cookies
import utils/utils, utils/crypt, utils/sha3h, utils/dbstorage, state, forms

type StaticFile = tuple[content, date, mimeType: string]
const NoStaticFile = (content:string(nil), date:string(nil), mimeType:string(nil))

let files {.global.} = newTable[string, StaticFile]()

proc initStaticFilesTable(root, default: string) =
    let contentTypes = newMimetypes()

    let appDir = getAppDir()
    let staticDir = appDir / root

    for filepath in walkDirRec(staticDir):
        let file = (
            content: readFile(filepath).string,
            date: getLastModificationTime(filepath).toRfcDate(),
            mimeType: contentTypes.getMimetype(splitFile(filepath).ext.trimStart('.'), "application/octet-stream"))

        let relative = "/" / filepath.substr(staticDir.len)
        files[relative] = file

        if relative == default:
            files["/"] = file

const HttpGet = "get"
const HttpPost = "post"

const ServerName = "nim " & NimVersion

proc send(req: Request, code: HttpCode, data: string, headers: varargs[tuple[key, val: string]]): Future[void] =
    let h = {
        "Date": getTime().toRfcDate(),
        "Server": ServerName}.newStringTable
    for key, val in items(headers): h[key] = val
    req.respond(code, data, h)

proc handleStaticFile(req: Request): Future[void] =
    if not eqIgnoreCase(req.reqMethod, HttpGet):
        req.send(Http405, "Method Not Allowed")
    else:
        let file = files.getOrDefault(req.url.path)
        if file == NoStaticFile:
            req.send(Http404, "Not Found")
        else:
            let headers = {
                "Accept-Ranges": "none",
                "Cache-Control": "max-age=300",
                "Content-Type": file.mimeType,
                "Date": file.date}
            req.send(Http200, file.content, headers)

type AuthData = tuple[login: string, pass: string]
const NoAuthData = (login:string(nil), pass:string(nil))

proc tryParseAuthData(req: Request): AuthData =
    try:
        let json = parseJson(req.body)
        (json["login"].getStr(), json["pass"].getStr())
    except:
        NoAuthData

proc handleAuthRequest(req: Request): Future[void] =
    if not eqIgnoreCase(req.reqMethod, HttpPost):
        return req.send(Http405, "Method Not Allowed")

    let auth = req.tryParseAuthData()
    if auth == NoAuthData:
        req.send(Http403, "Forbidden")
    elif auth.login.len < 4 or auth.login.len > 16 or auth.pass.len < 4 or auth.pass.len > 16:
        req.send(Http400, "Bad login/pass")
    elif addOrGetAuth(auth) != auth.pass:
        req.send(Http403, "Forbidden")
    else:
        req.send(Http200, "OK", {"Set-Cookie": "auth=$#:$#; path=/" % [$hmac_sha3(Key, auth.login).hex(), encodeUrl(auth.login)]})

proc tryAuth(req: Request): string =
    let cookies = try: parseCookies(req.headers.getOrDefault("Cookie")) except: newStringTable()
    let token = cookies.getOrDefault("auth")
    if isNilOrEmpty(token):
        return nil
    let auth = token.splitKeyValue(':')
    if isNilOrEmpty(auth.key) or isNilOrEmpty(auth.val):
        return nil
    let login = try: decodeUrl(auth.val) except: nil
    if isNil(login) or $hmac_sha3(Key, login).hex() != auth.key:
        return nil
    login

proc handleFormRequest(req: Request): Future[void] =
    if not eqIgnoreCase(req.reqMethod, HttpPost):
        return req.send(Http405, "Method Not Allowed")

    let login = tryAuth(req)
    if isNil(login):
        return req.send(Http403, "Forbidden")

    let json = if isNilOrEmpty(req.body): newJObject() else: (try: parseJson(req.body) except: nil)
    if isNil(json) or json.kind != JObject:
        return req.send(Http400, "Bad Request")

    let data = nextForm(login, json)
    if isNil(data.error):
        req.send(Http200, data.form)
    else:
        req.send(Http400, data.error)

proc handleLastRequest(req: Request): Future[void] =
    if not eqIgnoreCase(req.reqMethod, HttpGet):
        return req.send(Http405, "Method Not Allowed")

    let last =
        try: "[" & join(getLastJoins().filter(proc(ctz: JoinInfo): bool =
            ctz.public
        ).map(proc(ctz: JoinInfo): string =
            $(%*{ctz.login: ctz.join.toShortTime()})
        ), ",") & "]"
        except: "error"

    req.send(Http200, last)

proc route(req: Request): Future[void] =
    let path = req.url.path
    if path.startsWith("/auth/"):
        handleAuthRequest(req)
    elif path.startsWith("/form/"):
        handleFormRequest(req)
    elif path.startsWith("/last/"):
        handleLastRequest(req)
    else:
        handleStaticFile(req)

const MaxRequestLength = 8192

proc handle(req: Request) {.async.} =
    if not(isNil(req.body)) and req.body.len > MaxRequestLength:
        asyncCheck req.send(Http413, "Request Entity Too Large")
        return

    try: asyncCheck route(req)
    except: discard req.send(Http500, "Internal Server Error")

initStaticFilesTable("site/", "/index.html")

asyncCheck newAsyncHttpServer().serve(Port(80), handle)

#asyncdispatch sometimes throw exceptions :(
while true:
    try: runForever()
    except: discard
