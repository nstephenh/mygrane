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
		dblocation = home + ".Mygrane.db"
	}
	database, _ := sql.Open("sqlite3", dblocation)
	database.Prepare(`CREATE TABLE IF NOT EXISTS COMICS(
		id INTEGER PRIMARY KEY, title TEXT);

`)

}
