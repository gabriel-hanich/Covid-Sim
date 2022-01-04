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
                iterationList.reverse()
                showStats(iterationList, townData)
                found = true
            }
        }
        reader.readAsText(rawFiles[i])
    }

});


function showStats(iterationList, townData){
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
    for(var i=0; i<iterationList.length; i++){
        statusHTML += `
        <li class="iterationListItem">
            <div class="iterationItemContainer">
                <h3> ` + iterationList[i].iterationName + `</h3>
                <input type="checkbox" class="iterationCheckbox", id="iteration` + i + `" checked>
            </div>
        </li>
        `
    }
    
    statusHTML += `
            </ul>
        </div>
    </div>

    <button class="submitBtn" id="submitBtn">Submit</button>
    `

    statusContainer.innerHTML = statusHTML;

    setSubmitBtnListener(iterationList, townData);
}


function setSubmitBtnListener(thisIterationList, townData){
    var submitBtn = document.getElementById("submitBtn");
    submitBtn.addEventListener("click", function(event){
        console.log(document.getElementById("iteration0").checked)
        var selectedIterations = [];
        for(var i=0; i<thisIterationList.length; i++){
            if(document.getElementById("iteration" + i.toString()).checked){
                selectedIterations.push(thisIterationList[i])
            }
        }
        var dataWindow = window.open("/pages/viewer.html", "Data Viewer");
        setTimeout(function(){
            dataWindow.postMessage({"iterationList":selectedIterations, "townData": townData}, "http://127.0.0.1:5500/pages/viewer.html")
            dataWindow.focus()
        }, 100)
    });
}