package Mygrane

func Import(dir string, format string) string{
	switch format {
	case "0Day":
		return "Importing 0-Day"
		//do stuff
	case "CMC":
		return "Importing CMC"
		//do stuff
	default:
		return "Invalid Format"
	}
}