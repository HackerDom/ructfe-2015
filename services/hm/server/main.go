package main

import (
	"errors"
	"strings"
	"fmt"
	"net/http"
	"strconv"
	"time"
)

const (
	Unauthorized = "User is not authorized"
	AuthenticationFailed = "Authentication failed"
	Key = "f11ecd5521ddf2614e17e4fb074a86da" //todo
)

func addHealthMetrics(request *http.Request) (int, string) {

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
	return status, response
}

func getHealthMetrics(request *http.Request) (int, string) {

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
	return status, response
}

func addUser(request *http.Request) (int, string) {

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
	return status, response
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

func loggedin(request *http.Request) bool {
	_, err := getUserId(request)
	return err == nil
}

func extractUid(idStr string) string {
	id := decodeBase64(idStr)
	f := strings.FieldsFunc(id, split)
	return f[len(f)-1]
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

func login(request *http.Request) (int, string, http.Cookie, http.Cookie) {
	response := ""
	status := http.StatusTeapot
	var idCookie http.Cookie
	var authCookie http.Cookie
	
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
			authCookie = http.Cookie{Name : "auth", Value: auth, Expires: expire}
			idCookie = http.Cookie{Name : "id", Value: id, Expires: expire}
			response = fmt.Sprintf("Welcome, %v", user.Login)
		}
	}
	return status, response, authCookie, idCookie

}

func logout(request *http.Request) (int, string, http.Cookie, http.Cookie) {
	status := http.StatusOK
	expire := time.Now().AddDate(-1, 0, 0)
	authCookie := http.Cookie{Name : "auth", Value: "", Expires: expire}
	idCookie := http.Cookie{Name : "id", Value: "", Expires: expire} 
	response := "Bye-bye! Seeya!"

	return status, response, authCookie, idCookie
}