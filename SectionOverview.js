function onLoad(){
    var id = sessionStorage.getItem('SectionID')
    var id = 1
    var serviceURL = `http://localhost:5016/sectionoverview/${id}`
    displaySectionOverview(id)
}

function displaySectionOverview(SectionID){
    var request = new XMLHttpRequest();
    request.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            retrieveSectionOverview(this);
        }
    }
    request.open("GET", (`SectionOverview/${SectionID}`), false);
    request.setRequestHeader("Content-type", "application/json");
    request.send();
}

function retrieveSectionOverview(obj){
    
    var response_json = JSON.parse(obj.responseText);
    var tableHtml = ``;
    var enrolledList = response_json["data"]["courses"];
    sessionStorage.setItem('enrolledList', enrolledList)
    tableHtml += `<div>${Course Name}</div>`;
    for(element of enrolledList){
        //the code line below is to for loop to retrieve courseName using another function because right now only have courseID
        var retrieveCourseNameURL = `http://localhost:5016/sectionoverview/${element['CourseID']}`;
    }
    document.getElementById
}