var script = document.createElement('script');
script.src = 'http://jqueryjs.googlecode.com/files/jquery-1.2.6.min.js';
script.type = 'text/javascript';
document.getElementsByTagName('head')[0].appendChild(script);

function setMap(){
  window.map = "test";
}

function initialize() {
    var map_canvas = document.getElementById('map_canvas');
    var map_options = {
        center: new google.maps.LatLng(39.13858199058352, -86.5118408203125),
        zoom: 4,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    }
    window.map = new google.maps.Map(map_canvas, map_options);

    google.maps.event.addListener(map, 'click', function(event) {

        var selectedValues = [];    
        $("#selectBuses :selected").each(function(){
            selectedValues.push($(this).val()); 
        });
        var busList = JSON.stringify(selectedValues);
        //var busList = selectedValues.join();
        //Get the position of clicked point
        var formData = {  lat:event.latLng.lat(),
                          lng:event.latLng.lng(),
                          city: $('#selectUniv').val(),
                          busList: busList,
                          alertDistance: $('#alertDistance').val()
                        }
        $.post("/", formData);
        //TODO: why doesnt the event 'dblclick' stop propogating! x(
        //That is because the zoom has been already triggered before this line is executed.
        event.stop();
    });
}

google.maps.event.addDomListener(window, 'load', initialize);

function addMark(){
  alert($('#address').val());
}

function changeCity(univOptions, coordinates){
  var response;
  latLng = coordinates.split(':');
  window.map.setZoom(14);
  window.map.setCenter(new google.maps.LatLng( latLng[0], latLng[1] ) );
  $('#selectBuses').empty();
  $.get("/busList/" + univOptions, function(data){
    data = JSON.parse(data);
    for(i=0;i<data.length;i++){
      /// *** TODO check for better options for chk boxes in select
      $("#selectBuses").append(new Option(data[i], data[i]));
    }
    $('#busMapFrame').src = $('#busMap').val();
    
  });
}

var source = new EventSource("/alert");
/*eventSrc.addEventListener('busalert', function(data){
  alert("Bus: " + data + "near target location");
})*/
source.onmessage = function(event){
  alert(event.data);
}
