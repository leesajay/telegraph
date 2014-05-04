//-----------------------------------------------------------------------------
//Utility functions
//-----------------------------------------------------------------------------

function drawBarGraph(element, data){
	//TODO redraw if it already exists

	//split up the data into titles and values
	var dataset = [];
	var titles = [];
	for(var key in data){
		dataset.push(data[key]);
		titles.push(key);
	}

	var margin = {top: 20, right: 0, bottom: 20, left: 15},
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

	//fit the axes to the range of our data
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
		.attr("x", -6)
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
		.on('mouseout', tip.hide);
}
//-----------------------------------------------------------------------------

function currentlySuits(){
	//the likert scale viz
	//var data = {{currentlySuitsData}};
	//var data = {"car": {"stronglyAgree": 4, "agree": 5, "neutral": 9, "disagree": 15, "stronglyDisagree": 25},
	//	"bike": {"stronglyAgree": 4, "agree": 5, "neutral": 9, "disagree": 15, "stronglyDisagree": 25,},
	//	"transit": {"stronglyAgree": 4, "agree": 5, "neutral": 9, "disagree": 15, "stronglyDisagree": 25}};
	var element = d3.select("#currentlySuits");
	//TODO lables, tooltips, legend

	var cats = ["Strongly Disagree", "Disagree", "Neutal/No Answer", "Agree", "Strongly Agree"];
	var data = [
		{key:"Pedestrians", values:[25, 62, 22, 37, 41]},
		{key:"Cars", values:[36, 52, 36, 22, 61]},
		{key:"Transit", values:[31, 52, 41, 62, 41]},
		{key:"Bikes", values:[42, 26, 23, 34, 32]}
	];

	var n = 5, // number of layers
		m = data.length, // number of samples per layer
		stack = d3.layout.stack();

	//go through each layer, that's the range(n) part
	//then go through each object in data and pull out that objects's population data
	//and put it into an array where x is the index and y is the number
	var layers = stack(d3.range(n).map(function(d) { 
		var a = [];
		for (var i = 0; i < m; ++i) {
			a[i] = {x: i, y: data[i].values[d]};  
		}
		return a;
	}));

	//the largest single layer
	var yGroupMax = d3.max(layers, function(layer) { return d3.max(layer, function(d) { return d.y; }); });
	//the largest stack
	var yStackMax = d3.max(layers, function(layer) { return d3.max(layer, function(d) { return d.y0 + d.y; }); });

	//set up the tooltips TODO
//	var tip = d3.tip()
//		.attr('class', 'd3-tip')
//		.offset([-10, 0])
//		.html(function(d, i) {
//			return "<strong>" + cats[i] + "</strong> <span style='color:red'>" + data[Math.floor(1/5)].values[i%5] + "</span>";
//		});

	var margin = {top: 40, right: 60, bottom: 20, left: 40},
		width = 777 - margin.left - margin.right,
		height = 373 - margin.top - margin.bottom;

	var y = d3.scale.ordinal()
		.domain(d3.range(m))
		.rangeRoundBands([2, height], .08);

	var x = d3.scale.linear()
		.domain([0, yStackMax])
		.range([0, width]);

	var color = ["#CC0000", "#FF5050", "#FFFF66", "#19D119", "#009933"];

	var svg = element.append("svg")
		.attr("width", width + margin.left + margin.right)
		.attr("height", height + margin.top + margin.bottom)
		.append("g")
			.attr("transform", "translate(" + margin.left + "," + margin.top + ")");
//	svg.call(tip);

	var layer = svg.selectAll(".layer")
		.data(layers)
		.enter().append("g")
			.attr("class", "layer")
			.style("fill", function(d, i) { return color[i]; });

	var bar = layer.selectAll("g")
		.data(function(d) { return d; })
		.enter().append("g");

	bar.append("rect")
		.attr("y", function(d) { return y(d.x); })
		.attr("x", function(d) { return x(d.y0); })
		.attr("height", y.rangeBand())
		.attr("width", function(d) { return x(d.y); })
		.attr("class", "likertBar");
	//	.on('mouseover', tip.show)
	//	.on('mouseout', tip.hide);

	bar.append("text")
		.attr("x", function(d) { return x(d.y0) + 5; })
		.attr("y", function(d) { return y(d.x) + 10})
		.attr("dy", ".35em")
		.attr("font-family", "sans-serif")
		.attr("fill", "black")
		.text(function(d) { return d.y; });

	// Draw legend
	var legend = svg.append("g")
		.attr("class", "legend")
		.attr("height", 100)
		.attr("width", 100)
		.attr('transform', 'translate(-20,50)');

	var legendRect = legend.selectAll('rect').data(color);

	legendRect.enter()
		.append("rect")
		.attr("x", width - 30)
		.attr("width", 10)
		.attr("height", 10);

	legendRect
		.attr("y", function(d, i) {
			return i * 20;
		})
		.style("fill", function(d) {
			return d;
		});

	var legendText = legend.selectAll('text').data(cats);

	legendText.enter()
		.append("text")
		.attr("x", width - 10);

	legendText
		.attr("y", function(d, i) {
			return i * 20 + 9;
		})
		.text(function(d) {
			return d;
		});
 
}//function

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


function quotes(){
	//var data = ((quoteData}};
	var data = ["I sure do love that one thing", "I'm not too fond of that other thing", "It would be great if you'd do this third thing"];
	//an svg
	//three gs with title and circle
	//quotes in circle
	var headlines = ["Here's what one respondant likes about Telegraph:", "Here's what another respondant wishes were different:", "And here's an idea from yet another respondant:"];
	var width = 960;
	var height = 500;
	var margin = {left: 20; right: 0; top: 10; bottom: 0};
	var pad = 20;
	var xs = [];
	var r = 90;

	for(var i=0; i<3; i++){
		var x = r;
		if(i>0){
			x += (xs[i-1] + r + pad);
		}
		xs.push(x);
	}

	var svg = d3.select("#quotes").append("svg")
		.attr("width", width + margin.left + margin.right)
		.attr("height", height + margin.top + margin.bottom)
		.append("g")
			.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	/* Define the data for the circles */
	var blocks = svg.selectAll("g")
		.data(data)
		.enter()
		.append("g");

	block.append("h5")
		.text(function(d, i){return headlines[i];});

	/*Create and place "blocks" containing the circle and the text */   
	var circle = block
		.append("g")
		.attr("transform", function(d, i){return "translate("+xs[i]+", "+r+")"});

	/*Create the circle for each block */
	circle.append("circle")
		.attr("r", r)
		.attr("fill", "darkCyan");

	/* Create the text for each block */
	circle.append("text")
		.attr("dx", -20)
		.text(function(d){return d});
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
	var diagram = venn.drawD3Diagram(d3.select("#connectionToTele"), sets, 300, 300, {opacity: 0.9});
}
//-----------------------------------------------------------------------------
//main
//-----------------------------------------------------------------------------
currentlySuits();
highestPriority();
lowestPriority();
quotes();
useFrequency();
home();
primaryTransit();
connectionToTele();
