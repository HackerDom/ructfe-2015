import os, strutils, asynchttpserver, asyncdispatch, asyncnet, strtabs, tables, times, mimetypes, json
import utils/utils, utils/crypt

type StaticFile = tuple[content, date, mimeType: string]
const NoStaticFile = (content:nil, date:nil, mimeType:nil)

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

type Auth = tuple[login: string, pass: string]
const NoAuth = (login:nil, pass:nil)

proc tryParseAuth(req: Request): Auth =
    try:
        let json = parseJson(req.body)
        (json["login"].getStr(), json["pass"].getStr())
    except:
        (nil, nil)

proc handleAuthRequest(req: Request): Future[void] =
    if not eqIgnoreCase(req.reqMethod, HttpPost):
        req.send(Http405, "Method Not Allowed")
    else:
        let auth = req.tryParseAuth()
        if auth == NoAuth or auth.login != "admin":
            req.send(Http403, "Forbidden")
        else:
            req.send(Http200, "OK")

proc route(req: Request): Future[void] =
    if req.url.path.startsWith("/auth/"):
        handleAuthRequest(req)
    else:
        handleStaticFile(req)

proc handle(req: Request) {.async.} =
    var fail = false
    try:
        #echo req.url.path
        await route(req)
    except:
        #echo "Error: " & getCurrentExceptionMsg()
        fail = true

    if fail:
        await req.send(Http500, "Internal Server Error")

initStaticFilesTable("site/", "/index.html")

waitFor newAsyncHttpServer().serve(Port(8080), handle)
