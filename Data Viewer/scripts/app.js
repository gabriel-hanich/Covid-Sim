var formUpload = document.getElementById("fileUpload")

formUpload.addEventListener("change", function(event){
    var iterationList = [];
    var townDataList;
    var foundTownData = false;
    rawFiles = formUpload.files
    
    for(var i=0; i<rawFiles.length; i++){
        var reader = new FileReader();
        reader.onload = function (e){
            var thisData = JSON.parse(e.target.result);
            if(typeof thisData["townName"] != "undefined"){
                iterationList.push(thisData)
            }else{
                townData = thisData
                foundTownData = true;
            }
            if(iterationList.length == rawFiles.length - 1 && foundTownData){
                showStats(iterationList, townData)
            }
        }
        reader.readAsText(rawFiles[i])
    }
});


function showStats(iterationList, townData){
    console.log(townData)
    var statusContainer = document.getElementById("statusContainer");
    statusContainer.classList.remove("hidden");

    var statusHTML = ""
    statusHTML += `
        <h2>Town stats </h2>
        <h3>Town Name: ` + iterationList[0]["townName"] + `</h3>
        <h3>Population: ` + townData["general"][0]["population"] + `</h3>
        <h2>Iterations</h2>
    `

    statusContainer.innerHTML = statusHTML
}
