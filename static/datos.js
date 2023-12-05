var datoLuz = 0;
var datoTemperatura = 0;
var datoPuerta = 0;
var datoCalefaccion = 0;
var datoLuces = 0;
var datoCalefaccionAuto = 0;
var datoLucesAuto = 0;
var datoNombreNodo = 0;

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
        const { time, medicionLuz, medicionTemperatura,  encenderLuces, encenderCalefaccion,
            estaCalefaccionAutom, estaLucesAutom, estaPuertaAbierta, nombrenodo
        } = data;

        datoLuz = medicionLuz;
        datoTemperatura = +medicionTemperatura.toFixed(2);
        datoPuerta = estaPuertaAbierta;
        datoCalefaccion = encenderCalefaccion;
        datoLuces = encenderLuces;
        datoCalefaccionAuto = estaCalefaccionAutom;
        datoLucesAuto = estaLucesAutom;
        datoNombreNodo = nombrenodo;
    }


    function handleError(error) {
        console.error('Error al obtener datos:', error);
        datoLuz = null;
        datoTemperatura = null;
    }


    function scheduleNextRequest() {
        setTimeout(fetchDataAndUpdateChart, 3000); // Realiza la siguiente solicitud después de un segundo
    }


    // Inicia la función para realizar solicitudes HTTP periódicas
    fetchDataAndUpdateChart();


});

function actualizarDatosHtml() {
    document.getElementById("switchLucesAutom").checked = stringToBoolean(datoLucesAuto);
    document.getElementById("onOffLucesSwitch").checked = stringToBoolean
    document.getElementById("switchCalefaccionAutom").checked = stringToBoolean(datoCalefaccionAuto);
    document.getElementById("onOffcalefaccionSwitch").checked = stringToBoolean(datoCalefaccion);
}

function stringToBoolean(string) {
    switch (string.toLowerCase().trim()) {
        case "true": return true;
        case "false": return false;
        default: return Boolean(string);
    }
}