function initialize() {
    var map_canvas = document.getElementById('map_canvas');
    var map_options = {
        center: new google.maps.LatLng(44.5403, -78.5463),
        zoom: 8,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    }
    var map = new google.maps.Map(map_canvas, map_options);

    google.maps.event.addListener(map, 'dblclick', function(event) {
        //Get the position of clicked point
        window.alert(event.latLng);
        //TODO: why doesnt the event stop! x(
        event.stop();
    });
} 
google.maps.event.addDomListener(window, 'load', initialize);