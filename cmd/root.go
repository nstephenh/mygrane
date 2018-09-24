package cmd

import (
	"fmt"
	"github.com/spf13/cobra"
	"os"
)

var rootCmd = &cobra.Command{
	Use:   "mygrane",
	Short: "mygrane is a comics manager",
	Long: `mygrane is a comics manager. https://github.com/nstephenh/mygrane`,
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("Please specify a command: init, ls, import, help")
	},
}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}