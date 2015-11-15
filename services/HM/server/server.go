package main

import (
	"io"
	"flag"
	"fmt"
	"net/http"
	"html/template"
)

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
	render(w, "static/login.html")
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

var mux map[string]func(http.ResponseWriter, *http.Request)

type myHandler struct{}

func (*myHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	if h, ok := mux[r.URL.String()]; ok {
		h(w, r)
		return
	}

	io.WriteString(w, "My server: "+r.URL.String())
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

	server.ListenAndServe()
}