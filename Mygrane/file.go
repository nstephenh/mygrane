package Mygrane

import (
	"crypto/md5"
	"encoding/hex"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"regexp"
	"strconv"
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
	fdAccuaracy int //0 = no date, 1 = Year, 2 = Month , 3 = Day, 4 = From a 0-Day therefore this is the release date (99% confidence)
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
		zday, err  := regexp.Compile(`0-Day Week of ([12][90]\d\d.[01]\d.[0-3]\d)`)
		if str := zday.FindStringSubmatch(f.path); str != nil {
			//Strip the dots and convert to an integer
			f.fileDate, err = strconv.Atoi(strings.Replace(str[1], ".", "", 2))
			f.fdAccuaracy = 4
			f.DBUpdate()
			f.Print()
			return f, err
		}

	case "CMC":
		fmt.Println( "Importing CMC")
		//do stuff
	default:
		fmt.Println( "Invalid/Unknown Format")
	}
	//Default date grabbing
	rgx, err  := regexp.Compile(`([12][90]\d\d)`)
	if strs := rgx.FindAllString(f.path, -1); strs != nil {

		//Convert to an integer
		f.fileDate, err = strconv.Atoi(strs[len(strs)-1])
		f.fdAccuaracy = 1

	}else{
		f.fdAccuaracy = 0
	}
	f.DBUpdate()
	f.Print()
	return
}
func (f file) Print(){
	fmt.Print(f.path + " (" + f.hash + ") ")
	fmt.Print(" from date: " + strconv.Itoa(f.fileDate) + " ")
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