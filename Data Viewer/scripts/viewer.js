window.addEventListener("message", (event) => {
    if (event.origin !== "http://example.org:8080")
      console.log(event)
  
    // ...
  }, false);



function setUpLineGraph(id, dataSet, xLabel, yLabel){
    var overViewGraph = new Chart(id, {
        type: "line",
        data: {
            labels: xData,
            datasets: dataSet
        },
        options: {
            plugins: {
                legend: {
                    labels: {
                        color: "white", 
                    }
                }
            },
            scales: {
                y: {
                    ticks: {
                        color: 'white'
                    },
                    title: {
                        display: true,
                        text: yLabel,
                        color: "white"
                    }
                },
                x: {
                    ticks: {
                        color: "white"
                    },
                    title: {
                        display: true,
                        text: xLabel,
                        color: "white"
                    }
                }
            }
        }
    });
    
}

function getStandardData(xList, yList, label, index){
    return {
        label: label,
        data: yList,
        tension: 0,
        backgroundColor: colourList[index],
        borderColor: colourList[index]
    }
}

function resizeGraphs(){
    for(var i=0; i<graphList.length; i++){
        graphList[i][0].width = graphList[i][1].offsetWidth
        graphList[i][0].height = graphList[i][1].offsetHeight
    }
}

function findId(id, idList){
    for(var i=0; i<idList.length; i++){
        if(idList[i][id] == id){
            return idList[i]
        }
    }
}

var iterationData = JSON.parse(sessionStorage.getItem("iterations"));
var townData = JSON.parse(sessionStorage.getItem("townData"));

var colourList = ["#0E2431", "#304960", "#ab726f", "#6da545"];

var graphList = [];

window.addEventListener("resize", resizeGraphs);

//  Set up initial page data
document.getElementById("pageHeading").innerHTML = "<h1>" + iterationData[0]["townName"] + " Data</h1>"

// Init population makeup data
var populationStatsContainer = document.getElementById("populationStatsContainer");

for(var i=0; i<iterationData.length; i++){
    var totalInfectedList = []; 
    for(var day=0; day<iterationData[i]["simLength"]; day++){
        for(var person = 0; person<iterationData[i]["day" + (day + 1).toString()]["infectedPeopleID"].length; person++){
            if(totalInfectedList.includes(iterationData[i]["day" + (day + 1).toString()]["infectedPeopleID"][person]) == false){
                totalInfectedList.push(iterationData[i]["day" + (day + 1).toString()]["infectedPeopleID"][person])
            }
        }
    }



    var thisStatBox = document.createElement("div");
    thisStatBox.id = iterationData[i]["iterationName"] + "statBox";
    thisStatBox.classList.add("singleGraphContainer");
    thisStatBox.classList.add("singleStatContainer");
    populationStatsContainer.appendChild(thisStatBox);

    thisStatBox = document.getElementById(iterationData[i]["iterationName"] + "statBox");
    thisStatBox.innerHTML = `
        <h2>` + iterationData[i]["iterationName"] + ` Population statistics</h2>
        <div class="statTextBox">
            <h3>The average person was x years old</h3>
            <h3>An average person lived with x other people</h3>
            <br>
            <h3>A total of ` + totalInfectedList.length + ` people got infected</h3>
            <h3>The average covid patient was x years old</h3>
            <h3>The average infection lasted x days</h3>
            <h3>An average covid patient lived with x other people</h3>
        </div>
    `
}


// Create dailyCases chart
graphList.push([document.getElementById("dailyCasesGraph"), document.getElementById("dailyCasesContainer")])
graphList.push([document.getElementById("totalCasesGraph"), document.getElementById("totalCasesContainer")])
graphList.push([document.getElementById("dailyDeaths"), document.getElementById("dailyDeathsContainer")])
graphList.push([document.getElementById("totalDeaths"), document.getElementById("totalDeathsContainer")])
resizeGraphs();

console.log(iterationData)

dailyCasesDataSet = [];
totalCasesDataSet = [];
dailyDeathsDataSet = [];
totalDeathsDataSet = [];
for(var i=0; i<iterationData.length; i++){
    var xData = [];
    var dailyCases = [];
    var totalCases = [];
    var dailyDeaths = [];
    var totalDeaths = [];
    for(var k=0; k<iterationData[i]["simLength"]; k++){
        xData.push(k + 1);
        dailyCases.push(iterationData[i]["day" + (k+1).toString()]["stats"]["dailyCases"]);
        totalCases.push(iterationData[i]["day" + (k+1).toString()]["stats"]["totalActiveInfections"]);
        dailyDeaths.push(iterationData[i]["day" + (k+1).toString()]["stats"]["dailyDeaths"])
        totalDeaths.push(iterationData[i]["day" + (k+1).toString()]["stats"]["totalDeaths"])
    }

    dailyCasesDataSet.push(getStandardData(xData, dailyCases, iterationData[i]["iterationName"], i));
    totalCasesDataSet.push(getStandardData(xData, totalCases, iterationData[i]["iterationName"], i))
    dailyDeathsDataSet.push(getStandardData(xData, dailyDeaths, iterationData[i]["iterationName"], i))
    totalDeathsDataSet.push(getStandardData(xData, totalDeaths, iterationData[i]["iterationName"], i))
}


setUpLineGraph("dailyCasesGraph", dailyCasesDataSet, "Day", "Daily Covid Cases");
setUpLineGraph("totalCasesGraph", totalCasesDataSet, "Day", "Total Covid Cases");
setUpLineGraph("dailyDeaths", dailyDeathsDataSet, "Day", "Daily Deaths");
setUpLineGraph("totalDeaths", totalDeathsDataSet, "Day", "Total Deaths");
