// Rentlytics Exercise - Lease Visualizer
// ======================================
// Using the dataset below, build a lease history gantt chart.  The X-Axis should be time, with the Y-Axis representing
// unique "unitName" values.  On the gantt chart, each lease is represented by a rectangle, in the row corresponding to the unit.
// The graph should also highlight the month with the highest aggregated rent.
// 
// Please fork this CodePen to submit your result, you may use any HTML/CSS/JS preprocessors or framework you wish.
//
// DO NOT USE A CHARTING/GRAPHING LIBRARY (excluding D3).
var leaseData = [
    {
        "unitName": "A101",
        "beginTimestamp": 1328256000000,
        "endTimestamp": 1359978400000,
        "rent": 1200
    },
    {
        "unitName": "B201",
        "beginTimestamp": 1298966400000,
        "endTimestamp":   1398966400000,
        "rent": 1300
    },
    {
        "unitName": "A301",
        "beginTimestamp": 1275721200000,
        "endTimestamp": 1298966400000,
        "rent": 1500
    },
    {
        "unitName": "A101",
        "beginTimestamp":    1298966400000, 
        "endTimestamp": 1310664000000,
        "rent": 1100
    },
    {
        "unitName": "A301",
        "beginTimestamp": 1357878400000,
        "endTimestamp": 1369878400000,
        "rent": 2000
    }
];

//sort our array--this should really be done on the back end on data retrieval.  This is a pretty crappy sort.
function sortByName(a,b) {
  if (a.unitName < b.unitName)
     return -1;
  if (a.unitName > b.unitName)
    return 1;
  return 0;
}

function calculateWidth(timeDelta, maxTime, maxWidth) {
	var widthPercent = timeDelta / maxTime
	return Math.floor(widthPercent * maxWidth)
}

function calcuateLeftMargin(timeDelta, timeFrame, maxWidth) {
  var myMarginLeftPercent = timeDelta  / timeFrame
  return Math.floor(myMarginLeftPercent * maxWidth)
}

/* these should probably not be calculated in the buildChart function */
var firstTimestamp = 10000000000000 ;
var lastTimestamp = 0;
var timeFrame = 0;
var maxWidth = 0;

function buildChart()
{
	// Calculate some constants:
	// -timeFrame total seconds (miliseconds?) over the period we're interested in
	// -firstTimestamp -- earliest time we're interested in
	// -lastTimestamp -- latest time we're interested in.
	// -maxWidth -- maximum number of pixels we can chart in.
	
	//Find the time frame
	leaseData.sort(sortByName)
	leaseData.forEach(function(currentValue, index, array) {  
		if (firstTimestamp > currentValue.beginTimestamp)
		{ 
		  firstTimestamp = currentValue.beginTimestamp 
		}
	  if (lastTimestamp < currentValue.endTimestamp)
		{
			lastTimestamp = currentValue.endTimestamp
		}  
	})
	timeFrame = lastTimestamp - firstTimestamp;
	
	var container = $('#container')
	maxWidth = 0
	if (container.length > 0)
	{
		maxWidth = container[0].offsetWidth - 150;
	}
	
	//Render our chart
	var lastUnitName = ''
	var leftTimeOffset = firstTimestamp
	leaseData.forEach(function(currentValue, index, array) {
	  if (lastUnitName !== currentValue.unitName)
		{
		  var myLabel = $('<label for="item_' + index + '">' + currentValue.unitName + '</label>')
		  container.append(myLabel)
		  lastUnitName = currentValue.unitName
		  leftTimeOffset = firstTimestamp
		}      
	  
	  var myDiv = $('<div class="bar" id="item_' + index +'">'+currentValue.rent+'</div>')
	  var timeDelta
	  
	  timeDelta = currentValue.endTimestamp - currentValue.beginTimestamp;
	  var myWidth = calculateWidth(timeDelta, timeFrame, maxWidth)
	  
	  timeDelta = (currentValue.beginTimestamp - leftTimeOffset)
	  var myLeftMargin = calcuateLeftMargin(timeDelta, timeFrame, maxWidth)
	  
	  myDiv.animate({width: myWidth + 'px', marginLeft: myLeftMargin+'px'})
		container.append(myDiv)  
	  //Incase there are two bars for the same unit
	  leftTimeOffset = currentValue.endTimestamp
	})
}
buildChart()


function sortByBeginTimestamp(a,b) {
  if (a.beginTimestamp < b.beginTimestamp)
     return -1;
  if (a.beginTimestamp > b.beginTimestamp)
    return 1;
  return 0;
}

function checkApartmentEndDates(previousValue, currentValue, current)
{
	if (previousValue.endTimestamp <= currentValue.beginTimestamp){
		
        var itemToRemove = current['apartments'].indexOf(previousValue);
      	current['apartments'].splice(itemToRemove,1)
        // remove rent from the current rolling sum
        current['rentSum']-=previousValue.rent
      }    
}

function findHighestEarningMonth(leaseData)
{
	leaseData.sort(sortByBeginTimestamp)
	var highest = { 'rentSum': 0, 'apartments': [], 'rentDate': 0 }
	var previous = { 'rentSum': 0, 'apartments': [] }
	var current = { 'rentSum': 0, 'apartments': [] }
	
	leaseData.forEach(function(currentValue, index, array) {
		// TODO: test for prorated months

		//Copy our current apartments, leaving the object references intact  
		current['apartments'] = previous['apartments'].slice(0)
		
		// remove any apartments whose end date is before the current start date
		highest['apartments'].forEach(function(previousValue, previousIndex, previousArray){
			checkApartmentEndDates(previousValue, currentValue, current)
		})
	  
		// add our current apartment, and add its value to the sum
		current['apartments'].push(currentValue)
		current['rentSum'] += currentValue.rent

		// check if the current sum is higher than the current highest month 
		if (current['rentSum'] > highest['rentSum']){
			// record if it is
		  highest['rentSum'] = current['rentSum']
		  highest['rentDate'] = currentValue.beginTimestamp  
		}
		
		previous['apartments'] = current['apartments'].slice(0)
	})
	
	return highest
}

//print the months
function monthDiff(d1, d2) {
    var months;
    months = (d2.getFullYear() - d1.getFullYear()) * 12;
    months -= d1.getMonth() + 1;
    months += d2.getMonth();
    return months <= 0 ? 0 : months;
}
function printHighestEarningMonth()
{
	var months = $('#months')
	startMonth = new Date(firstTimestamp)
	numberOfMonths = monthDiff(startMonth, new Date(lastTimestamp))
	highestEarning = findHighestEarningMonth(leaseData)
	myMonth = $('<div class="month"></div>')
	
	var monthStart = new Date(highestEarning['rentDate'])
	monthStart.setDate(1)
	
	//copy month and add one to it
	var monthEnd = new Date(monthStart);
	monthEnd.setMonth(monthEnd.getMonth( ) + 1 );
	
	var timeDelta
	
	timeDelta = monthEnd.getTime() - monthStart.getTime()
	var myWidth = calculateWidth(timeDelta, timeFrame, maxWidth)
	
	timeDelta = monthEnd.getTime() - firstTimestamp
	var myLeftMargin = calcuateLeftMargin(timeDelta, timeFrame, maxWidth)
  
	myMonth.animate({width: myWidth + 'px', marginLeft: myLeftMargin+'px'})
	
	months.append(myMonth)
}

printHighestEarningMonth()
