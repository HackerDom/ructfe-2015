package main

import (
	"io"
	"flag"
	"fmt"
	"net/http"
)

func handleRequest(w http.ResponseWriter, request *http.Request) {
	response := "Cookies: "
		
	for _, cookie := range request.Cookies() {
		response += fmt.Sprintf("%v: %v\n", cookie.Name, cookie.Value)
		response += ";"
		fmt.Printf("%v: %v\n", cookie.Name, cookie.Value)
	}; fmt.Println("")
		
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

func main() {
	var port = flag.String("port", "8000", "please specify the port to start server on")
	flag.Parse()
	fmt.Println(*port)
	server := http.Server{
		Addr:    ":" + *port,
		Handler: &myHandler{},
	}

	mux = make(map[string]func(http.ResponseWriter, *http.Request))
	mux["/"] = handleRequest

	server.ListenAndServe()
}