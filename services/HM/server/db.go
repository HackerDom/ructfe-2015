package main

import (
	"database/sql"
//	"fmt"
	_ "github.com/mattn/go-sqlite3"
	"log"
	"os"
)
const DbName = "./health.db" 
const CreateTable = `
	CREATE TABLE index (id integer not null primary key, weight integer, bp integer, pulse integer, walking_distance integer, comment text);
	DELETE FROM index;
	`

func prepareDb() {
	os.Remove(DbName)

	db, err := sql.Open("sqlite3", DbName)
	if err != nil {
		log.Fatal("Error while connecting to db: ", err)
	}
	defer db.Close()

	_, err = db.Exec(CreateTable)
	if err != nil {
		log.Printf("%q: %s\n", err, CreateTable)
		return
	}

	// tx, err := db.Begin()
	// if err != nil {
		// log.Fatal(err)
	// }
	// stmt, err := tx.Prepare("insert into foo(id, name) values(?, ?)")
	// if err != nil {
		// log.Fatal(err)
	// }
	// defer stmt.Close()
	// for i := 0; i < 100; i++ {
		// _, err = stmt.Exec(i, fmt.Sprintf("こんにちわ世界%03d", i))
		// if err != nil {
			// log.Fatal(err)
		// }
	// }
	// tx.Commit()

	// rows, err := db.Query("select id, name from foo")
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
