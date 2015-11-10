package main

import (
	"strconv"
	"encoding/base64"
	"io"
	"flag"
	"fmt"
	"net/http"
)

func healthMetricsHandler(w http.ResponseWriter, request *http.Request) {

	metrics := parseFromForm(request)
	response := fmt.Sprintf("Comment from form: %v", metrics.Comment)
	io.WriteString(w, response)
}

func handleRequest(w http.ResponseWriter, request *http.Request) {
	response := "Response from server: "
	cookies := make(map[string]string)
		
	for _, cookie := range request.Cookies() {
		response += fmt.Sprintf("%v: %v;\n", cookie.Name, cookie.Value)
		fmt.Printf("%v: %v\n", cookie.Name, cookie.Value)
		cookies[cookie.Name] = cookie.Value
		if cookie.Name == "auth" {
			var authenticated = verifyAuthentication(cookie.Value)
			response += fmt.Sprintf("Authenticated: %v;\n", strconv.FormatBool(authenticated))
		}
	}; fmt.Println("")
	
	cookie := cookies["myCookie"]
	fmt.Println("myCookie: ", cookie)
		
	io.WriteString(w, response)
}

func verifyAuthentication(authCookie string) bool {
data, err := base64.StdEncoding.DecodeString(authCookie)
	if err != nil {
		fmt.Println("error:", err)
		return false
	}
	fmt.Println("Decoded data: ", data)
	return false
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

	prepareDb()
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

	server.ListenAndServe()
}