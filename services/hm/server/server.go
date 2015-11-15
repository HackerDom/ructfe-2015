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

func addHealthMetricsHandler(w http.ResponseWriter, request *http.Request) {

	status, response := addHealthMetrics(request)
	w.WriteHeader(status)
	io.WriteString(w, response)
}

func healthMetricsHandler(w http.ResponseWriter, request *http.Request) {

	status, response := getHealthMetrics(request)
	w.WriteHeader(status)
	io.WriteString(w, response)
}

func addUserHandler(w http.ResponseWriter, request *http.Request) {

	status, response := addUser(request)
	w.WriteHeader(status)
	io.WriteString(w, response)
}

func handleRequest(w http.ResponseWriter, request *http.Request) {
	render(w, "main.html")
}

func render(w http.ResponseWriter, tmpl string) {
    t, err := template.ParseFiles(tmpl)
    if err != nil {
        fmt.Println("template parsing error: ", err)
    }
    err = t.Execute(w, "")
    if err != nil {
        fmt.Println("template executing error: ", err)
    }
}

func loginHandler(w http.ResponseWriter, request *http.Request) {
	
	status, response, c1, c2 := login(request)
	http.SetCookie(w, &c1) 
	http.SetCookie(w, &c2) 
	w.WriteHeader(status)
	io.WriteString(w, response)

}

func logoutHandler(w http.ResponseWriter, request *http.Request) {
	
	status, response, c1, c2 := logout(request)
	http.SetCookie(w, &c1) 
	http.SetCookie(w, &c2) 
	w.WriteHeader(status)
	io.WriteString(w, response)
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

func initService(){
	prepareDb()
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
	mux["/"] = handleRequest
	mux["/healthMetrics"] = healthMetricsHandler
	mux["/addHealthMetrics"] = addHealthMetricsHandler
	mux["/newUser"] = addUserHandler
	mux["/login"] = loginHandler
	mux["/logout"] = logoutHandler
	mux["/static"] = staticHandler

	server.ListenAndServe()
}