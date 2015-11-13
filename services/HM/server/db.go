package main

import (
	"database/sql"
	"fmt"
	"strconv"
	_ "github.com/mattn/go-sqlite3"
	"log"
	"os"
)
const (
	DbName = "./health.db" 
	CreateIndicesTable = "CREATE TABLE healthIndices(id integer not null primary key AUTOINCREMENT, userId integer, weight integer, bp integer, pulse integer, walking_distance integer, comment text); DELETE FROM healthIndices;"
	InsertValues = "INSERT INTO healthIndices(userId, weight, bp, pulse, walking_distance, comment) VALUES (?, ?, ?, ?, ?, ?)"
	SelectRows = "SELECT id, comment FROM healthIndices WHERE userId = ?"
	
)

const (
	CreateUsersTable = "CREATE TABLE users(id integer not null primary key AUTOINCREMENT, login text, pass text); DELETE FROM users;"
	FindUser = "SELECT id, login FROM users WHERE login = ?"
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

	//todo: uId
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
	
	rows, err := db.Query(FindUser, user.Login)
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
	
	return Success, "u_" + strconv.FormatInt(id, 10)
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
	 _, err = stmt.Exec(i, i*3, i+3, (i-1)*4, fmt.Sprintf("Comment number %03d", i))
	 if err != nil {
		 log.Fatal(err)
	 }
	 }
	 tx.Commit()

	 rows, err := db.Query(SelectRows)
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

	// stmt, err = db.Prepare("select name from foo where id = ?")
	// if err != nil {
		// log.Fatal(err)
	// }
	// defer stmt.Close()
	// var name string
	// err = stmt.QueryRow("3").Scan(&name)
	// if err != nil {
		// log.Fatal(err)
	// }
	// fmt.Println(name)

	// _, err = db.Exec("delete from foo")
	// if err != nil {
		// log.Fatal(err)
	// }

	// _, err = db.Exec("insert into foo(id, name) values(1, 'foo'), (2, 'bar'), (3, 'baz')")
	// if err != nil {
		// log.Fatal(err)
	// }

	// rows, err = db.Query("select id, name from foo")
	// if err != nil {
		// log.Fatal(err)
	// }
	// defer rows.Close()
	// for rows.Next() {
		// var id int
		// var name string
		// rows.Scan(&id, &name)
		// fmt.Println(id, name)
	// }
}

func checkErr(err error) {
    if err != nil {
        panic(err)
    }
}
