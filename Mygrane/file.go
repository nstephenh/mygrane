package Mygrane

import (
	"crypto/md5"
	"encoding/hex"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
)

//statement, _ = database.Prepare(`CREATE TABLE IF NOT EXISTS Files(
//		id INTEGER PRIMARY KEY, path TEXT, hash TEXT, releaseGroup TEXT, fileDate REAL, fdAccuracy INT, comicID INTEGER, FOREIGN KEY(comicID) REFERENCES Comics(id));
//`)
type file struct{
	id int
	path string
	hash string
	rg string //release group
	fileDate int // Year (cover year if possible) that is in the file name
	fdAccuaracy int
	comicID int // for relational table
	tags []string
}

func NewFile(path string, info os.FileInfo, format string) (f *file, err error){
	f = new(file)

	f.path, err = filepath.Abs(path)
	os.Open(f.path)
	f.hash, err = hash_file_md5(f.path)
	f.tags = f.GetTags()
	switch format {
	case "0Day":
		fmt.Println( "Importing 0-Day")
		//do stuff
	case "CMC":

		fmt.Println( "Importing CMC")
		//do stuff
	default:
		fmt.Println( "Invalid Format")
	}
	f.DBUpdate()
	f.Print()
	return
}
func (f file) Print(){
	fmt.Print(f.path + " (" + f.hash + ") ")
	for _, tag := range f.tags{
		fmt.Print(tag + ", ")
	}
	fmt.Println()
}

func (f file)GetTags() []string{
	rawtags := strings.Split(filepath.Base(f.path), "(")
	tags :=  make([]string, len(rawtags)-1)
	for i, tag := range rawtags{
		if i == 0{ continue} // The first one is title
		tag = strings.Split(tag,")")[0]
		tags[i-1] = tag
	}
	return tags
}


//http://mrwaggel.be/post/generate-md5-hash-of-a-file-in-golang/
func hash_file_md5(filePath string) (string, error) {
	//Initialize variable returnMD5String now in case an error has to be returned
	var returnMD5String string

	//Open the passed argument and check for any error
	file, err := os.Open(filePath)
	if err != nil {
		return returnMD5String, err
	}

	//Tell the program to call the following function when the current function returns
	defer file.Close()

	//Open a new hash interface to write to
	hash := md5.New()

	//Copy the file in the hash interface and check for any error
	if _, err := io.Copy(hash, file); err != nil {
		return returnMD5String, err
	}

	//Get the 16 bytes hash
	hashInBytes := hash.Sum(nil)[:16]

	//Convert the bytes to a string
	returnMD5String = hex.EncodeToString(hashInBytes)

	return returnMD5String, nil

}