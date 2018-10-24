package Mygrane


//	statement, _ := database.Prepare(`CREATE TABLE IF NOT EXISTS Comics(
//		id INTEGER PRIMARY KEY, title TEXT, number TEXT, coverDate REAL, cdAccuracy INT,  releaseDate REAL, rdAccuaracy INT);
//`)

type comic struct{
	id int
	title string
	number string
	coverDate int
	cdAccuracy int
	releaseDate int
	rdAccuracy int
}

