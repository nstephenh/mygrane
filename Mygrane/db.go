package Mygrane

import (
	"database/sql"
	"fmt"
	_ "github.com/mattn/go-sqlite3"
	"github.com/mitchellh/go-homedir"
	"log"
	"os"
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
	 if false{
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
		path TEXT, hash TEXT UNIQUE PRIMARY KEY, title TEXT, number TEXT, releaseGroup TEXT, fileDate REAL, fdAccuracy INT, format INT, comicID INTEGER, FOREIGN KEY(comicID) REFERENCES Comics(ID));
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
	result, err := db.Exec(`INSERT OR REPLACE INTO Files(path, hash, title,  number, releaseGroup, fileDate, fdAccuracy, format) 
						 VALUES (?, ?, ?, ?, ?, ?, ?, ?)`, f.path, f.hash,  f.title, f.number, f.rg, f.fileDate, f.fdAccuaracy, f.format)
	if err != nil {
		log.Fatal(err)
	}
	rows, err := result.RowsAffected()
	if err != nil {
		log.Fatal(err)
	}
	if rows != 1 {
		panic(err)
	}

	for _, tag := range f.tags {
		db.Exec("INSERT INTO Tags(fileHash,tag) VALUES (?,?)", f.hash, tag)
	}
	db.Close()
}

func (c *comic)DBUpdate(){
	db, _ := sql.Open("sqlite3", dbloc)
	result, err := db.Exec(`INSERT OR REPLACE INTO Comics(title , number , coverDate , cdAccuracy , releaseDate , rdAccuaracy , isTPB) 
						 VALUES (?, ?, ?, ?, ?, ?, ?)`, c.title, c.number, c.coverDate, c.cdAccuracy, c.releaseDate, c.rdAccuracy, c.isTPB)
	if err != nil {
		log.Fatal(err)
	}
	rows, err := result.RowsAffected()
	if err != nil {
		log.Fatal(err)
	}
	if rows != 1 {
		panic(err)
	}
	db.Close()

}

func DB_Get_Files(filter string) (result []file) {
	db, _ := sql.Open("sqlite3", dbloc)
	fmt.Println("Querying DB")
	if rows, err := db.Query(`SELECT * FROM files`); err == nil {
		defer rows.Close()
		var result []file
		for rows.Next(){
			f := new(file)
			if err := rows.Scan(&f.path, &f.hash, &f.title, &f.number, &f.rg, &f.fileDate, &f.fdAccuaracy, &f.format, &f.comicID); err != nil {
				log.Fatal(err)
			}
			f.Print()
			result = append(result, *f)
		}
	}else{
		fmt.Println(err)
	}
	return
}


