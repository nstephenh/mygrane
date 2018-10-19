package cmd

import (
	"fmt"
	"github.com/mitchellh/go-homedir"
	"github.com/nstephenh/mygrane/Mygrane"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
	"os"
)

var rootCmd = &cobra.Command{
	Use:   "Mygrane",
	Short: "Mygrane is a comics manager",
	Long: `Mygrane is a comics manager. https://github.com/nstephenh/Mygrane`,
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("Please specify a command: ls, import, help")
	},
}

var cfgFile = "$HOME/.Mygrane"
var dbFile = "$HOME/.Mygrane.db"

func init() {
	cobra.OnInitialize(initConfig)
	rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "",
		"config file (default is $HOME/.Mygrane.yaml)")
	rootCmd.PersistentFlags().Bool("viper", true, "Use Viper for configuration")
	rootCmd.PersistentFlags().StringVar(&dbFile, "db", "",
		"database file (default is $HOME/.Mygrane.db")
}

func initConfig() {
	// Don't forget to read config either from cfgFile or from home directory!
	viper.SetConfigType("yaml")

	// Find home directory.
	home, err := homedir.Dir()

	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	if cfgFile != "" {
		// Use config file from the flag.
		viper.SetConfigFile(cfgFile)
		viper.SetConfigType("yaml")
	} else {

		// Search config in home directory

		viper.AddConfigPath(home)
		viper.SetConfigType("yaml")
		viper.SetConfigName(".Mygrane")
	}

	if err := viper.ReadInConfig(); err != nil {
		//if there's no config create a new one
		fmt.Println("Can't read config:", err)
		fmt.Println("Creating new config file at " + home + "/.Mygrane.yaml")
		if _, err := os.Create(home + "/.Mygrane.yaml"); err != nil {
			fmt.Println("Can't write default config:", err)
			os.Exit(1)
		}
	}
	Mygrane.Init_DB(dbFile)
}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}