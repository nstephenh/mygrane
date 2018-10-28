package cmd

import (
	"fmt"
	"github.com/nstephenh/mygrane/Mygrane"
	"github.com/spf13/cobra"
)

// importCmd represents the import command
var importCmd = &cobra.Command{
	Use:   "import",
	Short: "Import a comics directory into the database",
	Long: `Use this command to import one or more directories of comics. 
Use the format flag -f if the majority of your files deviate from standard naming conventions:
ex:
Comics/Iron Man 001 (2015) (release-group).cbz
Comics/Iron Man 002 (2015) (release-group).cbz

mygrane import Comics

or

CompleteMarvelChronology/1939/193900 Marvel Comics 001.cbz

mygrane import -f CMC CompleteMarvelChronology

`,
	Args: cobra.MinimumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("import called")
		for i:= 0; i < len(args); i++{
			fmt.Println("Importing Directory: " + args[i])
				Mygrane.Import(args[i], format)
		}
	},
}

var format = "0Day"

func init() {
	RootCmd.AddCommand(importCmd)

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// importCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// importCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")

	//var importme string;

	importCmd.Flags().StringVarP(&format, "format","f", "", `
Format for the imported files, can be:
0 = Default, "Title.cbz (year) (rg).cbz", may be in subdirectories by week
CMC = yyyymmdd Title num.cbz, may be in monthly/yearly subdirectores`)
}

