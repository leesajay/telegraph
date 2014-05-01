//-----------------------------------------------------------------------------
//Utility functions
//-----------------------------------------------------------------------------

function drawBarGraph(element, data){
	//redraw if it already exists
	//TODO ticks, tooltips

	//split up the data into titles and values
	var dataset = [];
	var titles = [];
	for(var key in data){
		dataset.push(data[key]);
		titles.push(key);
	}

	var margin = {top: 20, right: 0, bottom: 20, left: 10},
		width = 350 - margin.left - margin.right,
		height = 300 - margin.top - margin.bottom;

	//set up some stuff for the axis
	var x = d3.scale.ordinal()
		.rangeRoundBands([0, width], .1);
	var y = d3.scale.linear()
		.range([height, 0]);
	var xAxis = d3.svg.axis()
		.scale(x)
		.orient("bottom");
	var yAxis = d3.svg.axis()
		.scale(y)
		.tickSize(width)
		.orient("right");

	//set up the tooltips
	var tip = d3.tip()
		.attr('class', 'd3-tip')
		.offset([-10, 0])
		.html(function(d, i) {
			return "<strong>" + titles[i] + "</strong> <span style='color:red'>" + dataset[i] + "</span>";
		});
	//make the svg element
	var svg = element.append("svg")
		.attr("width", width + margin.left + margin.right)
		.attr("height", height + margin.top + margin.bottom)
		.append("g")
			.attr("transform", "translate(" + margin.left + "," + margin.top + ")");
	//I actually don't know what this does
	svg.call(tip);

	//fit the axes to the range of our data TODO is this necessary
	x.domain(titles);
	y.domain([0, d3.max(dataset)]);

	svg.append("g")
		.attr("class", "x axis")
		.attr("transform", "translate(0," + height + ")")
		.call(xAxis);

	var gy = svg.append("g")
		.attr("class", "y axis")
		.call(yAxis);

	gy.selectAll("g").filter(function(d) { return d; })
		.classed("minor", true);

	gy.selectAll("text")
		.attr("x", 4)
		.attr("dy", -4);

	//make the bars
	svg.selectAll(".bar")
		.data(dataset)
		.enter().append("rect")
			.attr("class", "bar")
			.attr("x", function(d, i) { return x(titles[i]); })
			.attr("width", x.rangeBand())
			.attr("y", function(d) { return y(d); })
			.attr("height", function(d) { return height - y(d); })
		.on('mouseover', tip.show)
		.on('mouseout', tip.hide)
}
//-----------------------------------------------------------------------------

function currentlySuits(){
	//the likert scale viz
	//var data = {{currentlySuitsData}};
	var data = {"car": {"stronglyAgree": 4, "agree": 5, "neutral": 9, "disagree": 15, "stronglyDisagree": 25},
		"bike": {"stronglyAgree": 4, "agree": 5, "neutral": 9, "disagree": 15, "stronglyDisagree": 25,},
		"transit": {"stronglyAgree": 4, "agree": 5, "neutral": 9, "disagree": 15, "stronglyDisagree": 25}};
	var element = d3.select("#currentlySuits");
	//TODO likert viz
	
}

function highestPriority(){
	//bar graph of highes priority
	//var data = {{highestPriorityData}};
	var data = {"cars": 24, "bikes": 125, "transit":73, "pedestrians":80};
	var element = d3.select("#highestPriority");
	drawBarGraph(element, data);
}

function lowestPriority(){
	//bar graph of lowest priority
	//var data = {{lowestPriorityData}};
	var data = {"cars": 24, "bikes": 125, "transit":73, "pedestrians":80};
	var element = d3.select("#lowestPriority");
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
	d3.select("#loveQuote").append("p").text(data);
}

function hateQuote(){
	//display the quote passed by python
	//var data = {{hateQuoteData}};
	var data = "I'm not too fond of that other thing";
	d3.select("#hateQuote").append("p").text(data);
}

function randomQuote(){
	//display the quote passed by python
	//var data = {{randomQuoteData}};
	var data = "It would be great if you'd do this third thing";
	d3.select("#randomQuote").append("p").text(data);
}

//-----------------------------------------------------------------------------
//TODO everything below this comment would work with static data; think about
//changing that

function useFrequency(){
	//bar chart of use frequency
	//var data = {{useFrequencyData}};
	var data = {"cars": 24, "bikes": 125, "transit":73, "pedestrians":80};
	var element = d3.select("#useFrequency");
	drawBarGraph(element, data);
}

function home(){
	//bar chart of home location
	//var data = {{homeData}};
	var data = {"cars": 24, "bikes": 125, "transit":73, "pedestrians":80};
	var element = d3.select("#home");
	drawBarGraph(element, data);
}

function primaryTransit(){
	//bar chart of primary transit
	//var data = {{primaryTransitData}};
	var data = {"cars": 24, "bikes": 125, "transit":73, "pedestrians":80};
	var element = d3.select("#primaryTransit");
	drawBarGraph(element, data);
}

function connectionToTele(){
	//venn diagram
	//var data = {{connectionToTeleData}};
	var data = {};
	//TODO venn diagram
	var sets = [{label: "Small", size: 10}, {label: "Big", size: 100}],
		overlaps = [{sets: [0,1], size: 5}];

	// get positions for each set
	sets = venn.venn(sets, overlaps);

	// draw the diagram
	var diagram = venn.drawD3Diagram(d3.select("#connectionToTele"), sets, 300, 300);

	// add the tooltip to the diagram NOTE killing for now
//	var tip = d3.tip().attr("class", "d3-tip").html(
//		function (d,i) { return "Size=" + d['size'];});

//	diagram.svg.call(tip);
//	diagram.text.style('cursor', 'default')
//		.on('mouseover', tip.show)
//		.on('mouseout', tip.hide);
}
//-----------------------------------------------------------------------------
//main
//-----------------------------------------------------------------------------
currentlySuits();
highestPriority();
lowestPriority();
loveQuote();
hateQuote();
randomQuote();
useFrequency();
home();
primaryTransit();
connectionToTele();
