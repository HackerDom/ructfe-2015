package main

import (
	"net/http"
)

type User struct {
	Login string
	Pass string
}

func parseUser(r *http.Request) *User {
	login := r.FormValue("Login")
	pass := r.FormValue("Pass")
	
    result := &User{login, pass}
	return result
}