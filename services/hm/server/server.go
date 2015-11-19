package main

import (
	"io"
	"flag"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"strings"
	"time"
)

const STATIC_URL string = "/static/"
const STATIC_ROOT string = "static/"
const LOG_FILE string = "log.txt"

type Link struct {
	LinkHref string
	LinkText string
}

type Context struct {
    LoggedIn bool
	Text string
	Metrics []HealthMetrics
}

func addHealthMetricsHandler(w http.ResponseWriter, request *http.Request) {

	status, response := addHealthMetrics(request)
	w.WriteHeader(status)

	context := Context{LoggedIn: loggedin(request), Text: response}
	render(w, "text", context)
}

func addHealthMetricsFormHandler(w http.ResponseWriter, request *http.Request) {
	context := Context{LoggedIn: loggedin(request)}
	render(w, "metrics", context)
}

func healthMetricsHandler(w http.ResponseWriter, request *http.Request) {

	status, response, metrics := getHealthMetrics(request)
	w.WriteHeader(status)
	
	if status == http.StatusOK {
		context := Context{LoggedIn: loggedin(request), Metrics: metrics}
		render(w, "table", context)
	} else {
		context := Context{LoggedIn: loggedin(request), Text: response}
		render(w, "text", context)
	}
}

func addUserHandler(w http.ResponseWriter, request *http.Request) {

	status, response := addUser(request)
	w.WriteHeader(status)
	
	context := Context{LoggedIn: loggedin(request), Text: response}
	render(w, "text", context)
}

func loginHandler(w http.ResponseWriter, request *http.Request) {
	
	status, response, c1, c2 := login(request)
	http.SetCookie(w, &c1) 
	http.SetCookie(w, &c2) 
	w.WriteHeader(status)
	
	loggedIn := status == http.StatusOK 

	context := Context{LoggedIn: loggedIn, Text: response}
	render(w, "text", context)
}

func logoutHandler(w http.ResponseWriter, request *http.Request) {
	
	status, response, c1, c2 := logout(request)
	http.SetCookie(w, &c1) 
	http.SetCookie(w, &c2) 
	w.WriteHeader(status)

	loggedIn := true
	if status == http.StatusOK {
		loggedIn = false
	}
	context := Context{LoggedIn: loggedIn, Text: response}
	render(w, "text", context)
}

func signupFormHandler(w http.ResponseWriter, request *http.Request) {
	context := Context{LoggedIn: loggedin(request)}
	render(w, "signup", context)
}

func loginformHandler(w http.ResponseWriter, request *http.Request) {
	context := Context{LoggedIn: loggedin(request)}
	render(w, "login", context)
}

func homeHandler(w http.ResponseWriter, request *http.Request) {
	context := Context{LoggedIn: loggedin(request)}
	render(w, "index", context)
}

func render(w http.ResponseWriter, tmpl string, context Context) {
    tmpl_list := []string{"templates/base.html",
        fmt.Sprintf("templates/%s.html", tmpl)}
    t, err := template.ParseFiles(tmpl_list...)
    if err != nil {
        logger.Println("template parsing error: ", err)
    }
    err = t.Execute(w, context)
    if err != nil {
        logger.Println("template executing error: ", err)
    }
}

func staticHandler(w http.ResponseWriter, req *http.Request) {
    static_file := req.URL.Path[len(STATIC_URL):]
    if len(static_file) != 0 {
        f, err := http.Dir(STATIC_ROOT).Open(static_file)
        if err == nil {
            content := io.ReadSeeker(f)
            http.ServeContent(w, req, static_file, time.Now(), content)
            return
        }
    }
    http.NotFound(w, req)
}

var mux map[string]func(http.ResponseWriter, *http.Request)

type myHandler struct{}

func (*myHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	path := "/" + strings.Split(r.URL.String(), "/")[1]
	if h, ok := mux[path]; ok {
		logger.Println("Incoming request: ", path, printForm(r))
		h(w, r)
		return
	}

	logger.Println("Warn: requested path not found:", path)
	http.Error(w, "404 page not found", 404)
}

func printForm(r *http.Request) string {
	if r.Method == "GET" {
		return ""
	}
	res := ""
	r.ParseForm()
    for key, _ := range r.Form {
        res += key + "=" + r.FormValue(key) + "; "
    }
	_, err := r.Cookie("id")
	if err != nil {
		res += "Id cookie was not set; "
	} else {
		res += "Id  cookie was set; "
	}
	_, err = r.Cookie("auth")
	if err != nil {
		res += "Auth cookie was not set; "
	} else {
		res += "Auth  cookie was set; "
	}
	return res
}

var links map[string]Link

var logger *log.Logger

func initService(){
	logger = setupLog(LOG_FILE)
	prepareDb()
}

func main() {

	initService()
	
	var port = flag.String("port", "8000", "please specify the port to start server on")
	flag.Parse()
	logger.Println("Port to start on: " + *port)
	server := http.Server{
		Addr:    ":" + *port,
		Handler: &myHandler{},
	}

	mux = make(map[string]func(http.ResponseWriter, *http.Request))
	mux["/"] = homeHandler
	mux["/healthmetrics"] = healthMetricsHandler
	mux["/addhealthmetrics"] = addHealthMetricsHandler
	mux["/addhealthmetricsform"] = addHealthMetricsFormHandler
	mux["/newuser"] = addUserHandler
	mux["/signupform"] = signupFormHandler
	mux["/login"] = loginHandler
	mux["/loginform"] = loginformHandler
	mux["/logout"] = logoutHandler
	mux["/static"] = staticHandler

	server.ListenAndServe()
}