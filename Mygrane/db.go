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
	dbloc = dblocation
	database, _ := sql.Open("sqlite3", dblocation)
	/*
	Database tables:
	Collections - groups of comics, can be titles, reading orders, etc
	rel_Collection_Comic - relation table between ^ and v
	Comics - Stores indivudal comics
	Files - Stores the individual instances of files, each cbz etc
	 */
	 if true{
	 	database.Exec("DROP TABLE Files; DROP TABLE Comics; Drop Table Collections; Drop Table Tags; DROP TABLE rel_Collection_Comic")
	 	fmt.Println("DEBUG: DROPPED ALL TABLES")
	 }



	statement, _ := database.Prepare(`CREATE TABLE IF NOT EXISTS Comics(
		id INTEGER PRIMARY KEY, title TEXT, number TEXT, coverDate REAL, cdAccuracy INT,  releaseDate REAL, rdAccuaracy INT, isTPB INT);
`)
	statement.Exec()
	statement, _ = database.Prepare(`CREATE TABLE IF NOT EXISTS Collections(
		id INTEGER PRIMARY KEY, title TEXT);
`)
	statement.Exec()

	statement, _ = database.Prepare(`CREATE TABLE IF NOT EXISTS Files(
		path TEXT, hash TEXT PRIMARY KEY, releaseGroup TEXT, fileDate REAL, fdAccuracy INT, comicID INTEGER, FOREIGN KEY(comicID) REFERENCES Comics(ID));
`)
	statement.Exec()

	statement, _ = database.Prepare(`CREATE TABLE IF NOT EXISTS rel_Collection_Comic(
		id INTEGER PRIMARY KEY, collectionID INTEGER , comicID INTEGER  , FOREIGN KEY(collectionID) REFERENCES Collections(id) , FOREIGN KEY(comicID) REFERENCES Comics(id));
`)
	statement.Exec()
	statement, _ = database.Prepare(`CREATE TABLE IF NOT EXISTS Tags(
		id INTEGER PRIMARY KEY, fileHash TEXT, tag TEXT, FOREIGN KEY(fileHash) REFERENCES Files(hash));
`)
	statement.Exec()
	database.Close()
	fmt.Println("Database Initiated")

}


func (f *file)DBUpdate(){
	db, _ := sql.Open("sqlite3", dbloc)
	db.Exec(`INSERT OR REPLACE INTO Files(path, hash, releaseGroup, fileDate, fdAccuracy) 
						 VALUES (?, ?, ?, ?, ?)`, f.path, f.hash, f.rg, f.fileDate, f.fdAccuaracy)
	//TODO: ADD tags
	for _, tag := range f.tags {
		db.Exec("INSERT INTO Tags(fileHash,tag) VALUES (?,?)", f.hash, tag)
	}
	db.Close()
}

