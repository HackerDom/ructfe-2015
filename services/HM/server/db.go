package main

import (
	"database/sql"
	"fmt"
	"strconv"
	_ "github.com/mattn/go-sqlite3"
	"log"
	"os"
	"errors"
)
const (
	DbName = "./health.db" 
	CreateIndicesTable = "CREATE TABLE healthIndices(id integer not null primary key AUTOINCREMENT, userId integer, weight integer, bp integer, pulse integer, walking_distance integer, comment text); DELETE FROM healthIndices;"
	InsertValues = "INSERT INTO healthIndices(userId, weight, bp, pulse, walking_distance, comment) VALUES (?, ?, ?, ?, ?, ?)"
	SelectRows = "SELECT id, comment FROM healthIndices WHERE userId = ?"
	SelectTopRows = "SELECT id, comment FROM healthIndices LIMIT 10"
	
)

const (
	CreateUsersTable = "CREATE TABLE users(id integer not null primary key AUTOINCREMENT, login text, pass text); DELETE FROM users;"
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
		log.Fatal("Error while connecting to db: ", err)
	}
	defer db.Close()
	
	stmt, err := db.Prepare(InsertValues)
	if err != nil {
		log.Fatal(err)
		return false, -1
	}
	
	res, err := stmt.Exec(uId, m.Weight, m.BloodPressure, m.Pulse, m.WalkingDistance, m.Comment) 
	if err != nil {
		log.Fatal(err)
		return false, -1
	}
	id, err := res.LastInsertId()
	if err != nil {
		log.Fatal(err)
		return false, -1
	}
	
	return true, id
}

func tryGetUserMetrics(uId string) (bool, []HealthMetrics) {

	var res []HealthMetrics
	
	db, err := sql.Open("sqlite3", DbName)
	if err != nil {
		log.Fatal("Error while connecting to db: ", err)
		return false, nil
	}
	defer db.Close()
	
	 stmt, err := db.Prepare(SelectRows)
	 if err != nil {
		log.Fatal(err)
		return false, nil
	 }
	 defer stmt.Close()
	 
	 rows, err := stmt.Query(uId)
	 if err != nil {
		log.Fatal(err)
		return false, nil
	 }
	 
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
		log.Fatal("Error while connecting to db: ", err)
	}
	defer db.Close()
	
	rows, err := db.Query(FindUserByLogin, user.Login)
	if err != nil {
		log.Fatal(err)
		return Error, ""
	}
	
	if rows.Next() {
		return AlreadyExists, ""
	}
	
	stmt, err := db.Prepare(AddUser)
	if err != nil {
		log.Fatal(err)
		return Error, ""
	}
	defer stmt.Close()
	
	res, err := stmt.Exec(user.Login, user.Pass) 
	if err != nil {
		log.Fatal(err)
		return Error, ""
	}
	id, err := res.LastInsertId()
	if err != nil {
		log.Fatal(err)
		return Error, ""
	}
	
	return Success, createUId(id)
}

func findUser(user *User) (string, error) {	
	db, err := sql.Open("sqlite3", DbName)
	if err != nil {
		log.Fatal("Error while connecting to db: ", err)
		return "", errors.New("Can't connect to DB")
	}
	defer db.Close()
	
	 stmt, err := db.Prepare(FindUser)
	 if err != nil {
		log.Fatal(err)
		return "", errors.New("Can't find user")
	 }
	 defer stmt.Close()
	 
	 rows, err := stmt.Query(user.Login, user.Pass)
	 if err != nil {
		log.Fatal(err)
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

func createUId(id int64) string {
	return "u_" + strconv.FormatInt(id, 10)
}

func prepareDb() {
	os.Remove(DbName)

	db, err := sql.Open("sqlite3", DbName)
	if err != nil {
		log.Fatal("Error while connecting to db: ", err)
	}
	defer db.Close()

	_, err = db.Exec(CreateIndicesTable)
	if err != nil {
		log.Printf("%q: %s\n", err, CreateIndicesTable)
		return
	}
	
	_, err = db.Exec(CreateUsersTable)
	if err != nil {
		log.Printf("%q: %s\n", err, CreateUsersTable)
		return
	}
	
	uid := addTestUser(db)
	addTestMetrics(db, uid) //debug
}

func addTestUser(db *sql.DB) string{
	stmt, err := db.Prepare(AddUser)
	if err != nil {
		log.Fatal(err)
		return ""
	}
	defer stmt.Close()
	
	res, err := stmt.Exec("testUser", "somePass") 
	if err != nil {
		log.Fatal(err)
		return ""
	}
	id, err := res.LastInsertId()
	if err != nil {
		log.Fatal(err)
		return ""
	}
	return createUId(id)
}

func addTestMetrics(db *sql.DB, uid string) {
	tx, err := db.Begin()
	 if err != nil {
		log.Fatal(err)
	 }
	 stmt, err := tx.Prepare(InsertValues)
	 if err != nil {
		log.Fatal(err)
	 }
	 defer stmt.Close()
	 
	 for i := 0; i < 5; i++ {
	 _, err = stmt.Exec(uid, i, i*3, i+3, (i-1)*4, fmt.Sprintf("Comment number %03d", i))
	 if err != nil {
		 log.Fatal(err)
	 }
	 }
	 tx.Commit()

	 rows, err := db.Query(SelectTopRows)
	 if err != nil {
		log.Fatal(err)
	 }
	 defer rows.Close()
	 
	 for rows.Next() {
		var id int
		var comment string
		rows.Scan(&id, &comment)
		fmt.Println(id, comment)
	 }
}

func checkErr(err error) {
    if err != nil {
        panic(err)
    }
}
