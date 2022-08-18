# mygrane
My Graphic Art Novel e-libary, or MyGrANe (pronounced migraine), is a python comic manager.
The current most useful feature is as a program to sort a directory of comics.

## DISCLAIMER: Mygrane is ABANDONWARE.
There is a GO version in the other branch. I don't remember what state it's in. 
I haven't used mygrane in 4+ years, and I wasn't using this version when I was, 
instead using an even older version I knew was stable.

Be careful with the sort, particularly sortdelete as there could be bugs that have unforseen consequences.
I have updated this to python3 and added some documentation so it can be used.

# Comic Naming Convention
Mygrane uses the names of comics to extract information about them, 
and will produce unexpected results if not named in this manner:

```
Title issuenumber (pubyear) (othertags).extension
```

Title - all text preceding the issuenumber.

issuenumber - The group of digits preceding the first parenthesis. Note that floats are supported.

pubyear - The year of publication of the comic, automatically determined by the last string in the filename matching
        the regex "\(([1-2][90]\d\d)\)"

othertags - Any number of strings that are enclosed by parenthesis in the filename.

extension - cbz, cbr, or pdf.

There are some scripts to use to convert from other naming conventions to the standard convention.

# Uses


## As a CLI app

The CLI for Mygrane is very basic.
Run `./Mygrane` or `python3 mygrane`
You will get a prompt `>`
Available commands:
```
    quit            Quits Mygrane
    init <path>     Initializes Library at path
    test            Runs a sort in "Test mode" where it does not move any files. Use "print" to see the result
    sort            Sorts library, not allowing duplicates
    sortdupes       Sorts library, allowing duplicates
    sortdelete      Sorts library, deleting duplicates
    print           Prints library contents
```

## As a library for a script
By writing a simple script, we can sort a collection of comics that use our naming convention.
location should be the path to your collection (absolute).
Your collection should be a directory of only comic files for the first run.
Empty directories or directories not following convention can produce unexpected results.
```python
from comic import Comic
from collection import Collection

location = "/the/path/to/your/collection"
stuff = Collection(location)
stuff.sort(test=False, allow_duplicates="True") 
#Change to allow_duplicates to "Delete" to delete duplicates (I'm not responsible if this deletes anything important)
print(stuff)
```
If you would like to run the program without moving any files, set test to True,
and then pipe the results of the script to a program such as less or more.

## As a graphical library for your comics
There is a gtk gui here. Don't use it. It's not up to date with everything else.

# How the sorting algorithm works
First, the program seperates all current objects between comics and series.
All the series objects are added to the new collection, while comics are added to a temporary collection for sorting.
The new collection is sorted by issue number.
The program checks each issue in the temporary collection against all the existing series and determines if meets the following crieteria:
   * The title is approximatly the same (ignoring changes in capitalization and punctuation)
   * The last issue in the series has the previous issue number (ex, issue
   * The last issue in the series was published before the checked issue
If either criteria isn't met, then a new series is made for the issue in question.

Make sure all files you are sorting follow the naming convention


