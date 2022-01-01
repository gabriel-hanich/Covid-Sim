var iterationData = JSON.parse(localStorage.getItem("iterations"));
var townData = JSON.parse(localStorage.getItem("townData"));

var colourList = ["#0E2431", "#304960", "#ab726f", "#6da545"]

//  Set up initial page data
document.getElementById("pageHeading").innerHTML = "<h1>" + iterationData[0]["townName"] + " Data</h1>"

// Create overview chart
var overViewGraph = document.getElementById("overViewGraph");
var overViewParent = document.getElementById("overViewContainer");
overViewGraph.width = overViewParent.offsetWidth;
overViewGraph.height = overViewParent.offsetHeight;

overViewGraphDataSet = [];

for(var i=0; i<iterationData.length; i++){
    console.log("YES")
    var xData = [];
    var yData = [];
    for(var k=0; k<iterationData[i]["simLength"]; k++){
        xData.push(k + 1);
        yData.push(iterationData[i]["day" + (k+1).toString()]["stats"]["dailyCases"]);
    }
    overViewGraphDataSet.push({
        label: "Iteration " + i.toString() + " Daily Cases",
        data: yData,
        tension: 0,
        backgroundColor: colourList[i],
        borderColor: colourList[i]
    });
}

var overViewGraph = new Chart("overViewGraph", {
    type: "line",
    data: {
        labels: xData,
        datasets: overViewGraphDataSet
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
                    text: 'Covid Cases (Daily)',
                    color: "white"
                }
            },
            x: {
                ticks: {
                    color: "white"
                },
                title: {
                    display: true,
                    text: 'Day Number',
                    color: "white"
                }
            }
        }
      }
});
