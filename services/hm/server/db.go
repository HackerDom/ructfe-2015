package main

import (
	"database/sql"
	_ "github.com/mattn/go-sqlite3"
	"errors"
	"sync"
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
	FindUser = "SELECT id FROM users WHERE login = ? AND pass = ?" 
	AddUser = "INSERT INTO users (login, pass) VALUES (?, ?)"
)

const (  
	Success = iota  
	Error = iota  
	AlreadyExists = iota  
)

var db *sql.DB
var m sync.Mutex

func tryAddMetrics(uId int, metrics *HealthMetrics) (bool, int64) {
	m.Lock()
	defer m.Unlock()
	
	stmt, err := db.Prepare(InsertValues)
	if err != nil {
		logger.Fatal(err)
		return false, -1
	}
	defer stmt.Close()
	
	res, err := stmt.Exec(uId, metrics.Weight, metrics.BloodPressure, metrics.Pulse, metrics.WalkingDistance, metrics.Comment) 
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
	m.Lock()
	defer m.Unlock()
	
	var res []HealthMetrics
	
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
	m.Lock()
	defer m.Unlock()
	
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
	m.Lock()
	defer m.Unlock()
	
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
	var err error
	db, err = sql.Open("sqlite3", DbName)
	checkErr(err)

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