package main

import (
	"strconv"
	"encoding/base64"
	"io"
	"flag"
	"fmt"
	"net/http"
)

func addHealthMetricsHandler(w http.ResponseWriter, request *http.Request) {

	response := ""
	metrics := parseFromForm(request)
	success, id := tryAddMetrics(metrics)
	if (success) {
		response = fmt.Sprintf("Metrics was successfully added, id assigned: %v", id)
	} else {
		response = "Metrics was not added"
	}
	io.WriteString(w, response)
}

func healthMetricsHandler(w http.ResponseWriter, request *http.Request) {

	response := ""
	uId := getUserId(request)
	success, metrics := tryGetUserMetrics(uId)
	if (success) {
		for _,m := range metrics {
			response += m.toString()
		}
	} else {
		response = "Metrics was not added"
	}
	io.WriteString(w, response)
}

func addUserHandler(w http.ResponseWriter, request *http.Request) {

	response := ""
	user := parseUser(request)
	result, uId := tryAddUser(user)
	if result == Success {
		response = fmt.Sprintf("User was successfully added, id assigned: %v", uId)
	} else if result == AlreadyExists {
		response = "User with this login already exists"
	} else {
		response = "Metrics was not added"
	}
	io.WriteString(w, response)
}

func getUserId(request *http.Request) string {
	return "" //
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

	server.ListenAndServe()
}