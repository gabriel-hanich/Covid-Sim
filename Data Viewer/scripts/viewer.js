var colourList = ["#0E2431", "#304960", "#ab726f", "#6da545"];

function setUpLineGraph(id, dataSet, xData, xLabel, yLabel){
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

function resizeGraphs(graphList){
    for(var i=0; i<graphList.length; i++){
        graphList[i][0].width = graphList[i][1].offsetWidth
        graphList[i][0].height = graphList[i][1].offsetHeight
    }
}

function findId(id, idList){
    var found = false;
    for(var i=0; i<idList.length; i++){
        if(idList[i]["id"] == id){
            return idList[i]
        }
    }
    if(!found){
        return NaN
    }
}

function getOccurrence(array, value) {
    var count = 0;
    array.forEach((v) => (v === value && count++));
    return count;
}


window.addEventListener("message", (event) => {
    var iterationData = event.data["iterationList"];
    var townData = event.data["townData"];
    generatePage(iterationData, townData)
}, false);

function generatePage(iterationData, townData){
    console.log(townData)
    console.log(townData["house"])
    var graphList = [];

    window.addEventListener("resize", resizeGraphs);

    //  Set up initial page data
    document.getElementById("pageHeading").innerHTML = "<h1>" + iterationData[0]["townName"] + " Data</h1>"

    // Init population makeup data
    var populationStatsContainer = document.getElementById("populationStatsContainer");
    var healthScoresContainer = document.getElementById("healthScoreGraphsContainer");

    for(var i=0; i<iterationData.length; i++){
        // Get list containing all covid patients (across whole simulation)
        var totalInfectedList = []; 
        
        var avgInfectionLength = 0;
        for(var day=0; day<iterationData[i]["simLength"]; day++){
            for(var person = 0; person<iterationData[i]["day" + (day + 1).toString()]["infectedPeopleID"].length; person++){
                personId = iterationData[i]["day" + (day + 1).toString()]["infectedPeopleID"][person]
                personData = findId(personId, townData["people"]);
                if(totalInfectedList.includes(personData) == false){
                    totalInfectedList.push(personData);
                    avgInfectionLength += iterationData[i]["day" + (day + 1).toString()]["peopleStates"][personId]["infectionLength"];
                }
            }
        }
        
        // Find averages
        var avgAge = 0;
        var avgResidentCount = 0;

        var avgInfectedAge = 0;
        var avgInfectedResidentCount = 0;
        for(var person=0; person<townData["people"].length; person++){
            personData = townData["people"][[person]];
            personAdress = findId(personData["adress"], townData["house"]);
            avgAge += personData["age"];
            avgResidentCount += personAdress["residentCount"];
            if(totalInfectedList.includes(personData)){
                avgInfectedAge += personData["age"];
                avgInfectedResidentCount += personAdress["residentCount"];
            }
        }

        avgAge = Math.round((avgAge / townData["general"][0]["population"]) * 100) / 100
        avgResidentCount = Math.round((avgResidentCount / townData["general"][0]["population"]) * 100) / 100

        avgInfectedAge = Math.round((avgInfectedAge / totalInfectedList.length) * 100) / 100
        avgInfectedResidentCount = Math.round((avgInfectedResidentCount / totalInfectedList.length) * 100) / 100
        avgInfectionLength =  Math.round((avgInfectionLength / totalInfectedList.length) * 100) / 100
    
        var thisStatBox = document.createElement("div");
        thisStatBox.id = iterationData[i]["iterationName"] + "statBox";
        thisStatBox.classList.add("singleGraphContainer");
        thisStatBox.classList.add("singleStatContainer");
        thisStatBox.classList.add("generated");
        populationStatsContainer.appendChild(thisStatBox);

        thisStatBox = document.getElementById(iterationData[i]["iterationName"] + "statBox");
        thisStatBox.innerHTML = `
            <h2><strong>` + iterationData[i]["iterationName"] + `</strong> Population statistics</h2>
            <div class="statTextBox">
                <h3>The average person was <strong>` + avgAge + `</strong> years old</h3>
                <h3>An average person lived in a household with  <strong>` + avgResidentCount + `</strong> people</h3>
                <br>
                <h3>A total of <strong>` + totalInfectedList.length + `</strong> people got infected</h3>
                <h3>The average covid patient was <strong>` + avgInfectedAge + `</strong> years old</h3>
                <h3>The average infection lasted <strong>` + avgInfectionLength +  `</strong> days</h3>
                <h3>An average covid patient lived in a household with  <strong>` + avgInfectedResidentCount + `</strong> people</h3>
            </div>
        `

        // Create healthscore scatter
        var thisHealthScoreContainer = document.createElement("div");
        thisHealthScoreContainer.classList.add("singleGraphContainer");
        thisHealthScoreContainer.classList.add("splitGraphContainer");
        thisHealthScoreContainer.innerHTML = `
            <h2><strong>` + iterationData[i]["iterationName"] + `</strong> Health Scores</h2>
                <div class="innerGraphContainer" id="iteration` + i + `healthScoreInner">
                    <canvas id="iteration` + i + `healthScoreGraph" class="graph" colours="colours"></canvas>
                </div>
        `
        
        healthScoresContainer.appendChild(thisHealthScoreContainer);

        var healthScoreDB = [];
        console.log(iterationData);
        for(var day=0; day<iterationData[i]["simLength"]; day++){
            var totalScores = [];
            var scores = [];
            for(var person = 0; person<iterationData[i]["day" + (day + 1).toString()]["infectedPeopleID"].length; person++){
                thisPersonID = iterationData[i]["day" + (day + 1).toString()]["infectedPeopleID"][person];
                thisPersonData = iterationData[i]["day" + (day + 1).toString()]["peopleStates"][thisPersonID];
                if(totalScores.includes(thisPersonData["healthScore"]) == false){
                    totalScores.push(thisPersonData["healthScore"])
                }
                scores.push(thisPersonData["healthScore"]);
            }
            for(var k=0; k<totalScores.length; k++){
                if(totalScores[k] != 0){
                    healthScoreDB.push({x:day, y:totalScores[k], r:(getOccurrence(scores, totalScores[k]) * 3)})
                }
            }

        }
        var healthScoreDB = {
            datasets: [{
              label: 'Health Scores',
              data: healthScoreDB,
              backgroundColor: colourList[i]
            }],
        };
        graphList.push([document.getElementById("iteration" + i + "healthScoreGraph"), document.getElementById("iteration" + i + "healthScoreInner")])
        resizeGraphs(graphList)
        var healthChart = new Chart("iteration" + i + "healthScoreGraph", {
            type: 'bubble',
            data: healthScoreDB,
            options: {
                scales: {
                    y: {
                        ticks: {
                            color: 'white'
                        },
                        title: {
                            display: true,
                            color: "white"
                        }
                    },
                    x: {
                        ticks: {
                            color: "white"
                        },
                        title: {
                            display: true,

                            color: "white"
                        }
                    }
                    
                }
            }
        })
    }

    // Create dailyCases chart
    graphList.push([document.getElementById("dailyCasesGraph"), document.getElementById("dailyCasesContainer")])
    graphList.push([document.getElementById("totalCasesGraph"), document.getElementById("totalCasesContainer")])
    graphList.push([document.getElementById("dailyDeaths"), document.getElementById("dailyDeathsContainer")])
    graphList.push([document.getElementById("totalDeaths"), document.getElementById("totalDeathsContainer")])
    resizeGraphs(graphList);

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


    setUpLineGraph("dailyCasesGraph", dailyCasesDataSet, xData, "Day", "Daily Covid Cases");
    setUpLineGraph("totalCasesGraph", totalCasesDataSet, xData, "Day", "Total Cases");
    setUpLineGraph("dailyDeaths", dailyDeathsDataSet, xData, "Day", "Total Deaths");
    setUpLineGraph("totalDeaths", totalDeathsDataSet, xData, "Day", "Total Deaths");
}

