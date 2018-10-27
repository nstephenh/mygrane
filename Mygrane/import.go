package Mygrane

import (
	"fmt"
	"os"
	"strings"
	"path/filepath"
)



func Import(dir string, format string)  (err error) {
	err = filepath.Walk(dir, func(path string, info os.FileInfo, err error) error{
		if err != nil {
			fmt.Printf("prevent panic by handling failure accessing a path %q: %v\n", path, err)
			return err
		}

		/* if info.IsDir() && info.Name() == subDirToSkip {
			fmt.Printf("skipping a dir without errors: %+v \n", info.Name())
			return filepath.SkipDir
		} */

		//Detect if is directory, if it follows naming conventions.
		// If so do a subwalk, excluding files already in that path.


		allowedExtensions := map[string]bool{
			".cbr":true,
			".cbz":true,
		}

		fmt.Printf("visited file or dir: %q\n", path)
		if !info.IsDir(){
			extension := strings.ToLower(filepath.Ext(info.Name()))
			fmt.Println(extension)
			if allowedExtensions[extension]{
				_, err = NewFile(path, info, format)
			}else{
				fmt.Printf("File does not have a valid extension, ignoring: %q\n", path)
			}
		}
		return nil
	})

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
	return
}
