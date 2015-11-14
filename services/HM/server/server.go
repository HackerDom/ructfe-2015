package main

import (
	"errors"
	"strings"
	"io"
	"flag"
	"fmt"
	"net/http"
	"strconv"
	"time"
	"html/template"
)

const (
	Unauthorized = "User is not authorized"
	AuthenticationFailed = "Authentication failed"
	Key = "f11ecd5521ddf2614e17e4fb074a86da" //todo
)

func addHealthMetricsHandler(w http.ResponseWriter, request *http.Request) {

	response := ""
	status := http.StatusTeapot
	
	uId, err := getUserId(request)
	if err != nil {
		status = http.StatusUnauthorized
		response = err.Error()
	} else {
		metrics := parseFromForm(request)
		userId, err := strconv.Atoi(strings.Split(uId, "_")[1])
		if err != nil {
			fmt.Println(err)
		}
		success, id := tryAddMetrics(userId, metrics)
		if (success) {
			status = http.StatusOK
			response = fmt.Sprintf("Metrics was successfully added, id assigned: %v", id)
		} else {
			status = http.StatusInternalServerError
			response = "Metrics was not added"
		}
	}
	w.WriteHeader(status)
	io.WriteString(w, response)
}

func healthMetricsHandler(w http.ResponseWriter, request *http.Request) {

	response := ""
	status := http.StatusTeapot
	
	uId, err := getUserId(request)
	if err != nil {
		status = http.StatusUnauthorized
		response = err.Error() 
	} else {
		response += uId // debug
		success, metrics := tryGetUserMetrics(uId)
		if success {
			status = http.StatusOK
			response += "; " + strconv.Itoa(len(metrics))
			for _,m := range metrics {
				response += m.toString()
			}
		} else {
			status = http.StatusInternalServerError
			response = "Can't get user's metrics"
		}
	}
	w.WriteHeader(status)
	io.WriteString(w, response)
}

func addUserHandler(w http.ResponseWriter, request *http.Request) {

	response := ""
	status := http.StatusTeapot
	
	user := parseUser(request)
	if user == nil {
		status = http.StatusBadRequest
		response = "Not enough parameters to add user"
	} else {	
		result, uId := tryAddUser(user)
		if result == Success {
			status = http.StatusOK
			response = fmt.Sprintf("User was successfully added, id assigned: %v", uId) //debug?
		} else if result == AlreadyExists {
			status = http.StatusConflict
			response = "User with this login already exists"
		} else {
			status = http.StatusInternalServerError
			response = "Metrics was not added"
		}
	}
	w.WriteHeader(status)
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
		return "", errors.New(AuthenticationFailed)
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

func authVerified(auth string, uId string) (bool, error) {

	id := decodeBase64(uId)
	
    res := md5hash(Key, id)

	if res == auth {
		return true, nil
	} else {
		return false, errors.New(Unauthorized)
	}
}

func loginHandler(w http.ResponseWriter, request *http.Request) {
	response := ""
	status := http.StatusTeapot
	
	user := parseUser(request)
	if user == nil {
		status = http.StatusBadRequest
		response = "You should specify both login and password"
	} else {	
		uid, err := findUser(user)
		if err != nil {
			status = http.StatusNotFound
			response = "There is no such user"
		} else {
			status = http.StatusOK
			expire := time.Now().AddDate(0, 0, 1)
			auth := md5hash(Key, uid)
			id := encodeBase64(uid)
			authCookie := http.Cookie{Name : "auth", Value: auth, Expires: expire}
			idCookie := http.Cookie{Name : "id", Value: id, Expires: expire}
			http.SetCookie(w, &authCookie) 
			http.SetCookie(w, &idCookie) 
			response = fmt.Sprintf("Welcome, %v", user.Login)
		}
	}
	w.WriteHeader(status)
	io.WriteString(w, response)

}

func logoutHandler(w http.ResponseWriter, request *http.Request) {
	status := http.StatusOK
	expire := time.Now().AddDate(-1, 0, 0)
	authCookie := http.Cookie{Name : "auth", Value: "", Expires: expire}
	idCookie := http.Cookie{Name : "id", Value: "", Expires: expire}
	http.SetCookie(w, &authCookie) 
	http.SetCookie(w, &idCookie) 
	response := "Bye-bye! Seeya!"

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