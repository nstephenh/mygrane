package cmd

import (
	"fmt"
	"github.com/mitchellh/go-homedir"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
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

var cfgFile = "$HOME/.mygrane"


func init() {
	cobra.OnInitialize(initConfig)
	rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file (default is $HOME/.mygrane.yaml)")
	rootCmd.PersistentFlags().Bool("viper", true, "Use Viper for configuration")
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
		viper.SetConfigName(".mygrane")
	}

	if err := viper.ReadInConfig(); err != nil {
		//if there's no config create a new one
		fmt.Println("Can't read config:", err)
		fmt.Println("Creating new config file")
		if _, err := os.Create(home + "/.mygrane.yaml"); err != nil {
			fmt.Println("Can't write default config:", err)
			os.Exit(1)
		}
	}
}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}