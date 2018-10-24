package Mygrane

import "crypto"

//statement, _ = database.Prepare(`CREATE TABLE IF NOT EXISTS Files(
//		id INTEGER PRIMARY KEY, path TEXT, hash TEXT, releaseGroup TEXT, fileDate REAL, fdAccuracy INT, comicID INTEGER, FOREIGN KEY(comicID) REFERENCES Comics(id));
//`)
type file struct{
	id int
	path string
	hash crypto.Hash
	rg string //release group
	fileDate int // Year (cover year if possible) that is in the file name
	fdAccuaracy int
	comicID int // for relational table
}
