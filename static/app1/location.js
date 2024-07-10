document.getElementById('login_form').onsubmit=function(event){
    event.preventDefault();
    
    if(navigator.geolocation){
        navigator.geolocation.getCurrentPosition(function(position){
            document.getElementById('lat').value=position.coords.latitude;
            document.getElementById('long').value=position.coords.longitude;
           document.getElementById('login_form').submit();
        }, function(error){
            alert('Cant retrive location,Please Turn on Location');
        });
    }
    else{
        alert ("Your browser doesn't support Geolocation");
    }
};