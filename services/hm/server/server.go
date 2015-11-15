package main

import (
	"io"
	"flag"
	"fmt"
	"html/template"
	"net/http"
	"strings"
	"time"
)

const STATIC_URL string = "/static/"
const STATIC_ROOT string = "static/"

type Link struct {
	LinkHref string
	LinkText string
}

type Context struct {
    Links []Link
	Action string
	Text string
}

func addHealthMetricsHandler(w http.ResponseWriter, request *http.Request) {

	status, response := addHealthMetrics(request)
	w.WriteHeader(status)

	linksToDisplay := []Link {links["mymetrics"], links["addmetrics"], links["logout"]}
	context := Context{Links: linksToDisplay, Action: "", Text: response}
	render(w, "text", context)
}

func addHealthMetricsFormHandler(w http.ResponseWriter, request *http.Request) {
	linksToDisplay := []Link {links["mymetrics"], links["addmetrics"], links["logout"]}
	context := Context{Links: linksToDisplay, Action: "/addhealthmetrics", Text: ""}
	render(w, "metrics", context)
}

func healthMetricsHandler(w http.ResponseWriter, request *http.Request) {

	status, response := getHealthMetrics(request)
	w.WriteHeader(status)
	io.WriteString(w, response)
}

func addUserHandler(w http.ResponseWriter, request *http.Request) {

	status, response := addUser(request)
	w.WriteHeader(status)
	
	linksToDisplay := []Link {links["login"], links["signup"]}
	context := Context{Links: linksToDisplay, Action: "", Text: response}
	render(w, "text", context)
}

func loginHandler(w http.ResponseWriter, request *http.Request) {
	
	status, response, c1, c2 := login(request)
	http.SetCookie(w, &c1) 
	http.SetCookie(w, &c2) 
	w.WriteHeader(status)
	
	var linksToDisplay []Link
	if status == http.StatusOK {
		linksToDisplay = []Link {links["mymetrics"], links["addmetrics"], links["logout"]}
	} else {
		linksToDisplay = []Link {links["login"], links["signup"]}
	}
	context := Context{Links: linksToDisplay, Action: "", Text: response}
	render(w, "text", context)
}

func logoutHandler(w http.ResponseWriter, request *http.Request) {
	
	status, response, c1, c2 := logout(request)
	http.SetCookie(w, &c1) 
	http.SetCookie(w, &c2) 
	w.WriteHeader(status)

	linksToDisplay := []Link {links["login"], links["signup"]}
	context := Context{Links: linksToDisplay, Action: "", Text: response}
	render(w, "text", context)
}

func signupFormHandler(w http.ResponseWriter, request *http.Request) {
	context := Context{Links: []Link{}, Action: "/newuser"}
	render(w, "login", context)
}

func loginformHandler(w http.ResponseWriter, request *http.Request) {
	context := Context{Links: []Link{}, Action: "/login"}
	render(w, "login", context)
}

func homeHandler(w http.ResponseWriter, request *http.Request) {
	context := Context{Links: getLinks(request)}
	render(w, "index", context)
}

func getLinks(request *http.Request) []Link {
	var linksToDisplay []Link
	if loggedin(request) {
		linksToDisplay = []Link {links["mymetrics"], links["addmetrics"], links["logout"]}
	} else {
		linksToDisplay = []Link {links["login"], links["signup"]}
	}
	return linksToDisplay
}

func render(w http.ResponseWriter, tmpl string, context Context) {
    tmpl_list := []string{"base.html",
        fmt.Sprintf("%s.html", tmpl)}
    t, err := template.ParseFiles(tmpl_list...)
    if err != nil {
        fmt.Println("template parsing error: ", err)
    }
    err = t.Execute(w, context)
    if err != nil {
        fmt.Println("template executing error: ", err)
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
	fmt.Println(path)
	if h, ok := mux[path]; ok {
		h(w, r)
		return
	}

	io.WriteString(w, "My server: "+path)
}

var links map[string]Link

func initService(){
	prepareDb()
	
	links = make(map[string]Link)
	links["login"] = Link{"/loginform", "Login"}
	links["signup"] = Link{"/signupform", "Sign Up"}
	links["logout"] = Link{"/logout", "Log Out"}
	links["mymetrics"] = Link{"/healthmetrics", "My Metrics"}
	links["addmetrics"] = Link{"/addhealthmetricsform", "Add Metrics"}
}

func main() {

	initService()
	
	var port = flag.String("port", "8000", "please specify the port to start server on")
	flag.Parse()
	fmt.Println("Port to start on: " + *port)
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
	//todo: about

	server.ListenAndServe()
}