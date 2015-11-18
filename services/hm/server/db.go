package main

import (
	"database/sql"
	"fmt"
	_ "github.com/mattn/go-sqlite3"
	"errors"
	"strconv"
)
const (
	DbName = "./health.db" 
	CreateIndicesTable = "CREATE TABLE IF NOT EXISTS healthIndices(id integer not null primary key AUTOINCREMENT, userId integer, weight integer, bp integer, pulse integer, walking_distance integer, comment text)"
	InsertValues = "INSERT INTO healthIndices(userId, weight, bp, pulse, walking_distance, comment) VALUES (?, ?, ?, ?, ?, ?)"
	SelectRows = "SELECT id, weight, bp, pulse, walking_distance, comment FROM healthIndices WHERE userId = ?"
	SelectTopRows = "SELECT id, comment FROM healthIndices LIMIT 10"
	
)

const (
	CreateUsersTable = "CREATE TABLE IF NOT EXISTS users(id integer not null primary key AUTOINCREMENT, login text, pass text)"
	FindUserByLogin = "SELECT id, login FROM users WHERE login = ?"
	FindUser = "SELECT id FROM users WHERE login = ? AND pass = ?" //todo
	AddUser = "INSERT INTO users (login, pass) VALUES (?, ?)"
)

const (  
	Success = iota  
	Error = iota  
	AlreadyExists = iota  
)


func tryAddMetrics(uId int, m *HealthMetrics) (bool, int64) {

	db, err := sql.Open("sqlite3", DbName)
	if err != nil {
		logger.Fatal("Error while connecting to db: ", err)
		return false, -1
	}
	defer db.Close()
	
	stmt, err := db.Prepare(InsertValues)
	if err != nil {
		logger.Fatal(err)
		return false, -1
	}
	defer stmt.Close()
	
	res, err := stmt.Exec(uId, m.Weight, m.BloodPressure, m.Pulse, m.WalkingDistance, m.Comment) 
	if err != nil {
		logger.Fatal(err)
		return false, -1
	}
	
	id, err := res.LastInsertId()
	if err != nil {
		logger.Fatal(err)
		return false, -1
	}
	
	return true, id
}

func tryGetUserMetrics(uId string) (bool, []HealthMetrics) {

	var res []HealthMetrics
	
	db, err := sql.Open("sqlite3", DbName)
	if err != nil {
		logger.Fatal("Error while connecting to db: ", err)
		return false, nil
	}
	defer db.Close()
	
	 stmt, err := db.Prepare(SelectRows)
	 if err != nil {
		logger.Fatal(err)
		return false, nil
	 }
	 defer stmt.Close()
	 
	 id := parseUId(uId)
	 
	 rows, err := stmt.Query(id)
	 if err != nil {
		logger.Fatal(err)
		return false, nil
	 }
	 defer rows.Close()
	 
	 for rows.Next() {
		var id int
		var weight int
		var bp int
		var pulse int
		var wd int
		var comment string
		rows.Scan(&id, &weight, &bp, &pulse, &wd, &comment)
		m := &HealthMetrics{weight, bp, pulse, wd, comment}
		res = append(res, *m)
	 }
	 return true, res
}

func tryAddUser(user *User) (int, string){

	db, err := sql.Open("sqlite3", DbName)
	if err != nil {
		logger.Fatal("Error while connecting to db: ", err)
		return Error, ""
	}
	defer db.Close()
	
	rows, err := db.Query(FindUserByLogin, user.Login)
	if err != nil {
		logger.Fatal(err)
		return Error, ""
	}
	defer rows.Close()
	
	if rows.Next() {
		return AlreadyExists, ""
	}
	
	stmt, err := db.Prepare(AddUser)
	if err != nil {
		logger.Fatal(err)
		return Error, ""
	}
	defer stmt.Close()
	
	res, err := stmt.Exec(user.Login, user.Pass) 
	if err != nil {
		logger.Fatal(err)
		return Error, ""
	}
	
	id, err := res.LastInsertId()
	if err != nil {
		logger.Fatal(err)
		return Error, ""
	}
	
	return Success, createUId(id)
}

func findUser(user *User) (string, error) {	

	db, err := sql.Open("sqlite3", DbName)
	if err != nil {
		logger.Fatal("Error while connecting to db: ", err)
		return "", errors.New("Can't connect to DB")
	}
	defer db.Close()
	
	 stmt, err := db.Prepare(FindUser)
	 if err != nil {
		logger.Fatal(err)
		return "", errors.New("Can't find user")
	 }
	 defer stmt.Close()
	 
	 rows, err := stmt.Query(user.Login, user.Pass)
	 if err != nil {
		logger.Fatal(err)
		return "", errors.New("Can't find user")
	 }
	 defer rows.Close()
	 
	 if rows.Next() {
		var id int64
		rows.Scan(&id)
		return createUId(id), nil
	 }
	 return "", errors.New("")
}

func prepareDb() {

	db, err := sql.Open("sqlite3", DbName)
	checkErr(err)
	defer db.Close()

	_, err = db.Exec(CreateIndicesTable)
	checkErr(err)
	
	_, err = db.Exec(CreateUsersTable)
	checkErr(err)
}

func checkErr(err error) {
    if err != nil {
		logger.Fatal(err)
        panic(err)
    }
}