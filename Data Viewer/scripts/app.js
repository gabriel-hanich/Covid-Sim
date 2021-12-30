var formUpload = document.getElementById("fileUpload")

formUpload.addEventListener("change", function(event){
    var iterationList = [];
    var townDataList;
    var foundTownData = false;
    rawFiles = formUpload.files
    var found = false;
    
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
                found = true
            }
        }
        reader.readAsText(rawFiles[i])
    }

});


function showStats(iterationList, townData){
    console.log("YES")
    var statusContainer = document.getElementById("statusContainer");
    statusContainer.classList.remove("hidden");
    
    var statusHTML = ""
    statusHTML += `
    <div class="statsContainer">
        <div class="townStats statContainer">
            <h2>Town stats </h2>
            <h3>Town Name: ` + iterationList[0]["townName"] + `</h3>
            <h3>Population: ` + townData["general"][0]["population"] + `</h3>
        </div>
        <div class="iterationStats statContainer">
        <h2>Iterations</h2>
        <ul class="iterationList">
    `
    console.log("HI")
    for(var i=0; i<iterationList.length; i++){
        console.log("REE")
        statusHTML += `
        <li class="iterationListItem">
            <div class="iterationItemContainer">
                <h3> ` + iterationList[i].iterationName + `</h3>
                <input type="checkbox" class="iterationCheckbox", id="iteration" + ` + i + ` checked>
            </div>
        </li>
        `
    }
    
    console.log("HI")
    statusHTML += `
            </ul>
        </div>
    </div>

    <button class="submitBtn">Submit</button>
    `

    console.log(statusHTML)
    statusContainer.innerHTML = statusHTML
}
