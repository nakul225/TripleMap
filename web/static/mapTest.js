var script = document.createElement('script');
script.src = 'http://jqueryjs.googlecode.com/files/jquery-1.2.6.min.js';
script.type = 'text/javascript';
document.getElementsByTagName('head')[0].appendChild(script);

function setMap(){
  window.map;
}

function initialize() {
    var map_canvas = document.getElementById('map_canvas');
    var map_options = {
        center: new google.maps.LatLng(39.13858199058352, -86.5118408203125),
        zoom: 12,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    }
    window.map = new google.maps.Map(map_canvas, map_options);

    google.maps.event.addListener(map, 'click', function(event) {
        //Get the position of clicked point
        $.post( "/", { lat:event.latLng.lat(), lng:event.latLng.lng()});
        //TODO: why doesnt the event 'dblclick' stop propogating! x(
        //That is because the zoom has been already triggered before this line is executed.
        event.stop();
    });
}

google.maps.event.addDomListener(window, 'load', initialize);

function addMark(){
  alert($('#address').val());
}


function changeCity(univOptions, cities){
  a = typeof(univOptions);
  //var map_canvas = document.getElementById('map_canvas');
  //window.alert(univOptions);
  //window.map.setCenter(new google.maps.LatLng( 45, 19 ) );
}

