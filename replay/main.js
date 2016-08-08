

// TODO Roll up the polling sections
//          Print just the last Pass or Fail
//          draw all locations
//


var eventData = null;

$(document).ready(function() {
  onLoad();
});

function onLoad() {
  var xhttp = new XMLHttpRequest();

  xhttp.onreadystatechange = function() {
    if (xhttp.readyState == 4 && xhttp.status == 200) {
      eventData = JSON.parse(xhttp.responseText);
      addList();
      imageBuilder();
    }
  };

  xhttp.open("GET", document.title + "_records.json", true);
  xhttp.send();
}

function imageBuilder() {
  $('body').on('mouseenter', '.type', function() {

    var source = "";
    var index = parseInt($(this).attr('id'));
    var snapIndex = eventData.records[index].image_id;

    source += eventData.snaps[snapIndex];
    var snap = new Image();
    snap.onload = function() {
        var finalCanvas = document.getElementById('surface');

        //Maintain original image aspect ratio
        var newHeight, newWidth;
        if(snap.height >= snap.width){
          newHeight = window.innerHeight - (window.innerHeight * 0.10);
          newWidth = Math.round(newHeight / (snap.height / snap.width));
        }
        else{
          newWidth = finalCanvas.width;
          newHeight = Math.round((snap.height / snap.width) * newWidth);
        }

        finalCanvas.setAttribute("width", newWidth);
        finalCanvas.setAttribute("height", newHeight);

        var canvas = document.createElement('canvas');

        canvas.setAttribute("width", snap.width);
        canvas.setAttribute("height", snap.height);

        var context = canvas.getContext("2d");
        context.clearRect(0, 0, snap.width, snap.height);
        context.drawImage(snap, 0, 0);

        for (var i = 0; i < eventData.records[index].locations.length; i++) {
          var x = eventData.records[index].locations[i].x;
          var y = eventData.records[index].locations[i].y;
          var width = eventData.records[index].locations[i].width;
          var height = eventData.records[index].locations[i].height;

          context.strokeStyle = "red";
          context.lineWidth = 5;
          context.strokeRect(x, y, width, height);
        }

        var finalContext = finalCanvas.getContext("2d");
        var img = new Image();
        img.onload = function() {
            finalContext.drawImage(img, 0, 0, newWidth, newHeight);
        }
        img.src = canvas.toDataURL();

    }
    snap.src = source;

  });
}

function addList() {
  var list = '<ul id=list>';

  for (var i = 0; i < eventData.records.length; i++) {
    list += "<li class=type " + "id=" + i + " data-toggle=tooltip title=\"" + eventData.records[i].message.replace(/"/g, '&quot;') + "\">" +
        eventData.records[i].type + "</li>";
  }
  list += '</ul>';
  $('#events').append(list);

  $('[data-toggle="tooltip"]').tooltip();
}