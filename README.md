# MyGrAne
My Graphic Art Novel e-libary, or MyGrANe (pronounced migraine), is a cli comic manager.

## Usage

Mygrane uses cobra for commands, and can accept a few.

### import
```
mygrane import [-f format] directory_or_file
```
Import will add any file in the specified directory to the database as a hash of the file, as well as any information it can gather from the name of the file and import directory.

### list
```
mygrane list
```
List lists all the comics in the database

## Preferred Comic Naming Convention
Mygrane uses the names of comics to extract information about them. This is the preferred naming convention:

```
Title issuenumber (pubyear) (othertags).extension
```

Title - all text preceding the issuenumber.

issuenumber - The group of digits preceding the first parenthesis. Note that floats are supported.

pubyear - The year of publication of the comic, automatically determined by the last string in the filename matching
        the regex "\(([1-2][90]\d\d)\)"

othertags - Any number of strings that are enclosed in parenthesis in the filename.

extension - cbz or cbr, case insensitive

### Other naming conventions 

```
yyyymmdd Title issuenumber.extension //This is referred to as cmc
```

