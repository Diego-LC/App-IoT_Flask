// Configuración del gráfico de Highcharts


// On chart load, start an interval that adds points to the chart and animate
// the pulsating marker.
const onChartLoad = function () {
const chart = this,
    series1 = chart.series[0],
    series2 = chart.series[1];

setInterval(function () {
    const x = (new Date()).getTime(), // current time
        y1 = datoTemperatura;
        y2 = datoLuz; // Asegúrate de tener este dato

    series1.addPoint([x, y1], true, true);
    series2.addPoint([x, y2], true, true); // Añade esta línea
}, 1000);
};


// Create the initial data
const data = (function () {
const data = [];
const time = new Date().getTime();


for (let i = -19; i <= 0; i += 1) {
    data.push({
        x: time + i * 1000,
        y: 0
    });
}
return data;
}());
const data2 = (function () {
const data = [];
const time = new Date().getTime();


for (let i = -19; i <= 0; i += 1) {
    data.push({
        x: time + i * 1000,
        y: Math.random() * 10
    });
}
return data;
}());


// Plugin to add a pulsating marker on add point
Highcharts.addEvent(Highcharts.Series, 'addPoint', e => {
    const point = e.point,
        series = e.target;


    if (!series.pulse) {
        series.pulse = series.chart.renderer.circle()
            .add(series.markerGroup);
    }

    setTimeout(() => {
        series.pulse
            .attr({
                x: series.xAxis.toPixels(point.x, true),
                y: series.yAxis.toPixels(point.y, true),
                r: series.options.marker.radius,
                opacity: 1,
                fill: series.color
            })
            .animate({
                r: 20,
                opacity: 0
            }, {
                duration: 1000
            });
    }, 1);
});




Highcharts.chart('container', {
    chart: {
        type: 'spline',
        events: {
            load: onChartLoad
        }
    },

    time: {
        useUTC: false
    },

    accessibility: {
        announceNewData: {
            enabled: true,
            minAnnounceInterval: 15000,
            announcementFormatter: function (allSeries, newSeries, newPoint) {
                if (newPoint) {
                    return 'New point added. Value: ' + newPoint.y;
                }
                return false;
            }
        }
    },

    xAxis: {
        type: 'datetime',
        tickPixelInterval: 150,
        maxPadding: 0.1
    },

    yAxis: {
        title: {
            text: 'Grado de Temperatura (°C) y Luz (Lux)'
        },
        plotLines: [
            {
                value: 0,
                width: 1,
                color: '#808080'
            }
        ]
    },

    tooltip: {
        headerFormat: '<b>{series.name}</b><br/>',
        pointFormat: '{point.x:%d-%m-%Y %H:%M:%S}<br/>{point.y:.2f} °C'
    },

    legend: {
        enabled: true, // Habilita la leyenda
        align: 'center', // Centra la leyenda
        verticalAlign: 'bottom', // Coloca la leyenda en la parte inferior
        layout: 'horizontal' // Dispone los elementos de la leyenda horizontalmente
    },

    exporting: {
        enabled: true // Habilita el botón de exportar
    },
    responsive: {
        rules: [{
            condition: {
                maxWidth: 250
            },
            chartOptions: {
                chart: {
                    height: 500
                },
                subtitle: {
                    text: null
                },
                navigator: {
                    enabled: false
                }
            }
        }]
    },
    title: {
        text: '',
        enabled: false
    },
    credits: {
        enabled: false
    },
    series: [
        {
            name: 'Temperatura',
            lineWidth: 2,
            color: Highcharts.getOptions().colors[2],
            data
        },
        {
            name: 'Luz',
            lineWidth: 2,
            color: Highcharts.getOptions().colors[1], // Cambia el color para diferenciar las líneas
            data: data2 // Asegúrate de tener los datos para esta serie
        }
    ]
});