var datoLuz = 0;
var datoTemperatura = 0;
var datoPuerta = 0;
var datoCalefaccion = 0;
var datoLuces = 0;
var datoCalefaccionAuto = 0;
var datoLucesAuto = 0;
var datoNombreNodo = 0;
var contador = 0;

document.addEventListener('DOMContentLoaded', function () {

    // Función para realizar solicitudes HTTP periódicas y actualizar el gráfico


    function fetchDataAndUpdateChart() {
        const apiUrl = 'http://34.239.209.214:8085/api/get_last_data';


        fetch(apiUrl)
            .then(handleResponse)
            .then(updateChart)
            .catch(handleError)
            .finally(scheduleNextRequest);
    }


    function handleResponse(response) {
        if (!response.ok) {
            throw new Error(`Error de red: ${response.status}`);
        }
        else{
            return response.json();
        }
    }


    function updateChart(data) {
        console.log(data);
        console.log(data.medicionLuz);
        const {medicionLuz, medicionTemperatura,  encenderLuces, encenderCalefaccion,
            encendidoAutomaticoCalefaccion, encendidoAutomaticoLuces, estaPuertaAbierta
        } = data;
        

        datoLuz = medicionLuz;
        datoTemperatura = +medicionTemperatura.toFixed(2);
        datoPuerta = estaPuertaAbierta;
        datoCalefaccion = encenderCalefaccion;
        datoLuces = encenderLuces;
        datoCalefaccionAuto = encendidoAutomaticoCalefaccion;
        datoLucesAuto = encendidoAutomaticoLuces;
    }


    function handleError(error) {
        console.error('Error al obtener datos:', error);
        datoLuz = null;
        datoTemperatura = null;
    }


    function scheduleNextRequest() {
        setTimeout(fetchDataAndUpdateChart, 1000); // Realiza la siguiente solicitud después de un segundo
        contador++;
    }


    // Inicia la función para realizar solicitudes HTTP periódicas
    fetchDataAndUpdateChart();


});

function actualizarDatosHtml() {
    document.getElementById("switchLucesAutom").checked = stringToBoolean(datoLucesAuto.toString());
    document.getElementById("onOffLucesSwitch").checked = stringToBoolean(datoLuces.toString());
    document.getElementById("switchCalefaccionAutom").checked = stringToBoolean(datoCalefaccionAuto.toString());
    document.getElementById("onOffcalefaccionSwitch").checked = stringToBoolean(datoCalefaccion.toString());
}

function stringToBoolean(string) {
    if(string.toLowerCase().trim() === "true")
        return true;
    else
        return false;
        
}