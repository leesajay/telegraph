//-----------------------------------------------------------------------------
//Utility functions
//-----------------------------------------------------------------------------

function drawBarGraph(element, data){
	//redraw if it already exists
	//TODO
}
//-----------------------------------------------------------------------------

function currentlySuits(){
	//the likert scale viz
	//var data = {{currentlySuitsData}};
	var data = {"car": {"stronglyAgree": 4, "agree": 5, "neutral": 9, "disagree": 15, "stronglyDisagree": 25},
		"bike": {"stronglyAgree": 4, "agree": 5, "neutral": 9, "disagree": 15, "stronglyDisagree": 25,},
		"transit": {"stronglyAgree": 4, "agree": 5, "neutral": 9, "disagree": 15, "stronglyDisagree": 25}};
	var element = document.getElementById("currentlySuits");
	//TODO likert viz
	
}

function highestPriority(){
	//bar graph of highes priority
	//var data = {{highestPriorityData}};
	var data = {"cars": 24, "bikes": 125, "transit":73, "pedestrians":80};
	var element = document.getElementById("highestPriority");
	drawBarGraph(element, data);
}

function lowestPriority(){
	//bar graph of lowest priority
	//var data = {{lowestPriorityData}};
	var data = {"cars": 24, "bikes": 125, "transit":73, "pedestrians":80};
	var element = document.getElementById("lowestPriority");
	drawBarGraph(element, data);
}

function updateOpinions(){
	//update everything in the opinions pane: takes a list of datasets that Python
	//already dealt with
	//var dataList = {{updateOpinionsData}};
	var dataList = {"lowestPriority": {"cars": 24, "bikes": 125, "transit":73, "pedestrians":80},
		"highestPriority": {"cars": 24, "bikes": 125, "transit":73, "pedestrians":80},
		"currentlySuits": {"car": {"stronglyAgree": 4, "agree": 5, "neutral": 9, "disagree": 15, "stronglyDisagree": 25},
			"bike": {"stronglyAgree": 4, "agree": 5, "neutral": 9, "disagree": 15, "stronglyDisagree": 25,},
			"transit": {"stronglyAgree": 4, "agree": 5, "neutral": 9, "disagree": 15, "stronglyDisagree": 25}}}
	//for each list in that list of lists
		//call drawGraph on the element and the list of data
	for(var key in dataList){
		var data = dataList[key];
		var element = document.getElementById(key);
		drawBarGraph(element, data);
	}
}

//-----------------------------------------------------------------------------
//javascript wouldn't have to get involved if we wanted to just refresh this
//every time, but ajax is much cleaner
//hold up, I have no idea how to serve this data from flask without reloading
//TODO how to do an ajax call with flask, which I think actually came up in 
//the webarch project - look at that

function loveQuote(){
	//display the quote passed by python
	//var data = {{loveQuoteData}};
	var data = "I sure do love that one thing";
	document.getElementById("loveQuote").innerHTML = data;
}

function hateQuote(){
	//display the quote passed by python
	//var data = {{hateQuoteData}};
	var data = "I'm not too fond of that other thing";
	document.getElementById("hateQuote").innerHTML = data;
}

function randomQuote(){
	//display the quote passed by python
	//var data = {{randomQuoteData}};
	var data = "It would be great if you'd do this third thing";
	document.getElementById("randomQuote").innerHTML = data;
}

//-----------------------------------------------------------------------------
//TODO everything below this comment would work with static data; think about
//changing that

function useFrequency(){
	//bar chart of use frequency
	//var data = {{useFrequencyData}};
	var data = {"cars": 24, "bikes": 125, "transit":73, "pedestrians":80};
	var element = document.getElementById("useFrequency");
	drawBarGraph(element, data);
}

function home(){
	//bar chart of home location
	//var data = {{homeData}};
	var data = {"cars": 24, "bikes": 125, "transit":73, "pedestrians":80};
	var element = document.getElementById("home");
	drawBarGraph(element, data);
}

function primaryTransit(){
	//bar chart of primary transit
	//var data = {{primaryTransitData}};
	var data = {"cars": 24, "bikes": 125, "transit":73, "pedestrians":80};
	var element = document.getElementById("primaryTransit");
	drawBarGraph(element, data);
}

function connectionToTele(){
	//venn diagram
	//var data = {{connectionToTeleData}};
	var data = {};
	var element = document.getElementById("connectionToTele");
	//TODO venn diagram
	
}

