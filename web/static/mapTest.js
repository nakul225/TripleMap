var script = document.createElement('script');
script.src = 'http://jqueryjs.googlecode.com/files/jquery-1.2.6.min.js';
script.type = 'text/javascript';
document.getElementsByTagName('head')[0].appendChild(script);

function initialize() {
    var map_canvas = document.getElementById('map_canvas');
    var map_options = {
        center: new google.maps.LatLng(39.13858199058352, -86.5118408203125),
        zoom: 12,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    }
    var map = new google.maps.Map(map_canvas, map_options);

    google.maps.event.addListener(map, 'dblclick', function(event) {
        //Get the position of clicked point
        window.alert(event.latLng);
        //window.location = event.latLng;
        //TODO: why doesnt the event stop! x(
        event.stop();
    });
}

google.maps.event.addDomListener(window, 'load', initialize);

function addMark(){
  alert($('#address').val());
}

