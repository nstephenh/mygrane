package Mygrane

import (
	"database/sql"
	"fmt"
	"github.com/mitchellh/go-homedir"
	"os"
	_ "github.com/mattn/go-sqlite3"
)

func Init_DB(dblocation string) {
	if dblocation == ""{
		home, err := homedir.Dir()

		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}
		dblocation = home + "/" + ".Mygrane.db"
	}
	database, _ := sql.Open("sqlite3", dblocation)
	/*
	Database tables:
	Collections - groups of comics, can be titles, reading orders, etc
	rel_Collection_Comic - relation table between ^ and v
	Comics - Stores indivudal comics
	rel_Comic_File - relation table between ^ and v
	Files - Stores the individual instances of files, each cbz etc
	 */

	statement, err := database.Prepare(`CREATE TABLE IF NOT EXISTS COMICS(
		id INTEGER PRIMARY KEY, title TEXT);

`)
	fmt.Println(err)
	statement.Exec()
	statement, _ = database.Prepare(`CREATE TABLE IF NOT EXISTS COLLECTIONS(
		id INTEGER PRIMARY KEY, title TEXT);
`)
	statement.Exec()

	statement, _ = database.Prepare(`CREATE TABLE IF NOT EXISTS FILES(
		id INTEGER PRIMARY KEY, path TEXT, hash TEXT);
`)
	statement.Exec()
	fmt.Println("Database Initiated")



}
