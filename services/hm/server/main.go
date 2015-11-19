package main

import (
	"errors"
	"strings"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"
)

const (
	Unauthorized = "User is not authorized"
	AuthenticationFailed = "Authentication failed"
)

const Key string = "f11ecd5521ddf2614e17e4fb074a86da"

func addHealthMetrics(request *http.Request) (error) {
	
	uId, err := getUserId(request)
	if err != nil {
		logger.Println("Can't get user from request")
		return err
	}
	
	metrics := parseFromForm(request)
	if metrics == nil {
		logger.Println("Can't parse metrics from request")
		return errors.New("Can't parse metrics from your request")
	}
	
	userId, err := strconv.Atoi(strings.Split(uId, "_")[1])
	if err != nil {
		logger.Println("Can't parse user Id: ", err)
		return errors.New("Can't find user to add metrics for")
	}

	success, _ := tryAddMetrics(userId, metrics)
	if (success) {
		return nil
	} else {
		return errors.New("Metrics were not added")
	}
}

func getHealthMetrics(request *http.Request) ([]HealthMetrics, error) {

	var metrics []HealthMetrics
	
	uId, err := getUserId(request)
	if err != nil {
		return metrics, err
	} else {
		var success bool
		success, metrics = tryGetUserMetrics(uId)
		if success {
			return metrics, nil
		} else {
			return metrics, errors.New("Can't get user's metrics")
		}
	}
}

func addUser(request *http.Request) (string, error) {
	
	user := parseUser(request)
	if user == nil {
		return "", errors.New("Not enough parameters to add user")
	} else {	
		result, uId := tryAddUser(user)
		if result == Success {
			return fmt.Sprintf("User was successfully added, id assigned: %v", uId), nil
		} else if result == AlreadyExists {
			return "", errors.New("User with this login already exists")
		} else {
			return "", errors.New("Metrics were not added")
		}
	}
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

func login(request *http.Request) ( string, http.Cookie, http.Cookie) {
	response := ""
	var idCookie http.Cookie
	var authCookie http.Cookie
	
	user := parseUser(request)
	if user == nil {
		response = "You should specify both login and password"
	} else {	
		uid, err := findUser(user)
		if err != nil {
			response = "There is no such user"
		} else {
			expire := time.Now().AddDate(1, 0, 0)
			auth := md5hash(Key, uid)
			id := encodeBase64(uid)
			authCookie = http.Cookie{Name : "auth", Value: auth, Expires: expire}
			idCookie = http.Cookie{Name : "id", Value: id, Expires: expire}
			response = fmt.Sprintf("Welcome, %v", user.Login)
		}
	}
	return response, authCookie, idCookie

}

func logout(request *http.Request) (http.Cookie, http.Cookie) {
	expire := time.Now().AddDate(-1, 0, 0)
	authCookie := http.Cookie{Name : "auth", Value: "", Expires: expire}
	idCookie := http.Cookie{Name : "id", Value: "", Expires: expire} 

	return authCookie, idCookie
}

func setupLog(filename string) *log.Logger{
	var logwriter io.Writer
	file, err := os.OpenFile(filename, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
	if err != nil {
		fmt.Println("Failed to open log file", err)
		logwriter = os.Stdout
	}
	
	logwriter = file

	logger := log.New(logwriter, "", log.Ldate|log.Ltime|log.Lshortfile)
	return logger
}