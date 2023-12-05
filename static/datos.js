var datoLuz = 0;
var datoTemperatura = 0;
var datoPuerta = 0;
var datoCalefaccion = "false";
var datoLuces = "true";
var datoCalefaccionAuto = "false";
var datoLucesAuto = "false";
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
        const {medicionLuz, medicionTemperatura,  encenderLuces, encenderCalefaccion,
            encendidoAutomaticoCalefaccion, encendidoAutomaticoLuces, estaPuertaAbierta
        } = data;
        console.log("dato luz auto: " + encendidoAutomaticoLuces);
        console.log("dato calefaccion auto: " + encendidoAutomaticoCalefaccion);
        console.log("dato luz: " + encenderLuces);
        console.log("dato calefaccion: " + encenderCalefaccion);
        console.log("--------------------");

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
    datoLucesAuto = stringToBoolean(datoLucesAuto.toString());
    datoCalefaccionAuto = stringToBoolean(datoCalefaccionAuto.toString());
    datoLuces = stringToBoolean(datoLuces.toString());
    datoCalefaccion = stringToBoolean(datoCalefaccion.toString());
    document.querySelector("#switchLucesAutom").checked = datoLucesAuto;
    document.querySelector("#onOffLucesSwitch").checked = datoLuces;
    document.querySelector("#switchCalefaccionAutom").checked = datoCalefaccionAuto;
    document.querySelector("#onOffcalefaccionSwitch").checked = datoCalefaccion;
    console.log("-----------actualiazado switeches----------");
    console.log("Switch luces auto: " + datoLucesAuto);
    console.log("Switch calefaccion auto: " + datoCalefaccionAuto);
    console.log("Switch luces: " + datoLuces);
    console.log("Switch calefaccion: " + datoCalefaccion);
}

function stringToBoolean(string) {
    if(string.toLowerCase().trim() == "true")
        return true;
    else
        return false;
        
}