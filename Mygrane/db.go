package Mygrane

import (
	"database/sql"
	"fmt"
	"github.com/mitchellh/go-homedir"
	"os"
	_ "github.com/mattn/go-sqlite3"
)

var dbloc string // Global Variable that holds the database file location.

func Init_DB(dblocation string) {
	if dblocation == ""{
		home, err := homedir.Dir()

		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}
		dblocation = home + "/" + ".Mygrane.db"
	}
	dbloc = dblocation;
	database, _ := sql.Open("sqlite3", dblocation)
	/*
	Database tables:
	Collections - groups of comics, can be titles, reading orders, etc
	rel_Collection_Comic - relation table between ^ and v
	Comics - Stores indivudal comics
	rel_Comic_File - relation table between ^ and v
	Files - Stores the individual instances of files, each cbz etc
	 */

	statement, _ := database.Prepare(`CREATE TABLE IF NOT EXISTS Comics(
		id INTEGER PRIMARY KEY, title TEXT);

`)
	statement.Exec()
	statement, _ = database.Prepare(`CREATE TABLE IF NOT EXISTS Collections(
		id INTEGER PRIMARY KEY, title TEXT);
`)
	statement.Exec()

	statement, _ = database.Prepare(`CREATE TABLE IF NOT EXISTS Files(
		id INTEGER PRIMARY KEY, path TEXT, hash TEXT, releaseGroup TEXT);
`)
	statement.Exec()

	statement, _ = database.Prepare(`CREATE TABLE IF NOT EXISTS rel_Collection_Comic(
		id INTEGER PRIMARY KEY, collectionID INTEGER , comicID INTEGER  , FOREIGN KEY(collectionID) REFERENCES Collections(id) , FOREIGN KEY(Comic) REFERENCES Comics(id));
`)
	statement.Exec()

	statement, _ = database.Prepare(`CREATE TABLE IF NOT EXISTS rel_Comic_File(
  		id INTEGER PRIMARY KEY, comicID INTEGER, pathID INTEGER, FOREIGN KEY(comicID) REFERENCES Comics(id) , FOREIGN KEY(pathID) REFERENCES Files(id) );
`)
	statement.Exec()
	database.Close()
	fmt.Println("Database Initiated")

}


func Add_File(){
	db, _ := sql.Open("sqlite3", dbloc)
	db.Prepare("")
	db.Close()
}