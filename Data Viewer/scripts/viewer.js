
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

var iterationData = JSON.parse(localStorage.getItem("iterations"));
var townData = JSON.parse(localStorage.getItem("townData"));

var colourList = ["#0E2431", "#304960", "#ab726f", "#6da545"];

var graphList = [];

window.addEventListener("resize", resizeGraphs);

//  Set up initial page data
document.getElementById("pageHeading").innerHTML = "<h1>" + iterationData[0]["townName"] + " Data</h1>"

// Create dailyCases chart
graphList.push([document.getElementById("dailyCasesGraph"), document.getElementById("dailyCasesContainer")])
graphList.push([document.getElementById("totalCasesGraph"), document.getElementById("totalCasesContainer")])
graphList.push([document.getElementById("dailyDeaths"), document.getElementById("dailyDeathsContainer")])
graphList.push([document.getElementById("totalDeaths"), document.getElementById("totalDeathsContainer")])
resizeGraphs();

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
    console.log(dailyDeaths)
    dailyCasesDataSet.push(getStandardData(xData, dailyCases, iterationData[i]["iterationName"], i));
    totalCasesDataSet.push(getStandardData(xData, totalCases, iterationData[i]["iterationName"], i))
    dailyDeathsDataSet.push(getStandardData(xData, dailyDeaths, iterationData[i]["iterationName"], i))
    totalDeathsDataSet.push(getStandardData(xData, totalDeaths, iterationData[i]["iterationName"], i))
}


setUpLineGraph("dailyCasesGraph", dailyCasesDataSet, "Day", "Daily Covid Cases");
setUpLineGraph("totalCasesGraph", totalCasesDataSet, "Day", "Total Covid Cases");
setUpLineGraph("dailyDeaths", dailyDeathsDataSet, "Day", "Daily Deaths");
setUpLineGraph("totalDeaths", totalDeathsDataSet, "Day", "Total Deaths");


console.log(iterationData)