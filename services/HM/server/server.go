package main

import (
	"errors"
	"strings"
	"io"
	"flag"
	"fmt"
	"net/http"
)

const (
	Unauthorized = "User is not authorized"
	Key = ""
)

func addHealthMetricsHandler(w http.ResponseWriter, request *http.Request) {

	response := ""
	//uId, err := getUserId(request)
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
	uId, err := getUserId(request)
	if err != nil {
		response = err.Error() //todo
	} else {
		response += uId
		success, metrics := tryGetUserMetrics(uId)
		if (success) {
			for _,m := range metrics {
				response += m.toString()
			}
		} else {
			response = "Metrics was not added"
		}
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

func getUserId(request *http.Request) (string, error) {
	authCookie, err := request.Cookie("auth")
	if err != nil {
		return "", errors.New(Unauthorized)
	}
	auth := authCookie.Value
	
	idCookie, err := request.Cookie("id")
	if err != nil {
		return "", errors.New(Unauthorized)
	}
	id := idCookie.Value
	
	verified, err := authVerified(auth, id)
	if err != nil {
		return "", errors.New("Can't get user id")
	}
	if verified {
		uId := extractUid(id)
		return uId, nil
	} else {
		return "", errors.New(Unauthorized)
	}
}

func extractUid(idStr string) string {
	id := decodeBase64(idStr)
	f := strings.FieldsFunc(id, split)
	return f[len(f)-1]
}

func handleRequest(w http.ResponseWriter, request *http.Request) {
	response := "Response from server: "
	uId, err := getUserId(request)
	if err != nil {
		response += err.Error()
	} else {
		response += uId
	}
	io.WriteString(w, response)
}

func authVerified(auth string, uId string) (bool, error) {

	id := decodeBase64(uId)
	
    res := md5hash(Key, id)

	if res == auth {
		return true, nil
	} else {
		return false, errors.New(Unauthorized)
	}
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