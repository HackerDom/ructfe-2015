package main

import (
	"net/http"
	"strconv"
	"strings"
)

type User struct {
	Login string
	Pass string
}

func parseUser(r *http.Request) *User {
	login := r.FormValue("Login")
	pass := r.FormValue("Pass")
	
	if login == "" || pass == "" {
		return nil
	}
    result := &User{login, pass}
	return result
}

func createUId(id int64) string {
	return "u_" + strconv.FormatInt(id, 10)
}

func parseUId(uId string) int {
	res, err := strconv.Atoi(strings.Split(uId, "_")[1])
	if err != nil {
		logger.Fatal("Can't parse uId=", uId)
	}
	return res
}