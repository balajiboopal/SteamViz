function getHighchartsData() {
    var chartData = [];
    if (typeof Highcharts !== "undefined" && Highcharts.charts) {
        Highcharts.charts.forEach(function (chart, index) {
            if (chart && chart.series) {
                chartData.push({
                    chartIndex: index,
                    series: chart.series.map(function (series) {
                        return {
                            name: series.name,
                            data: series.options.data,
                        };
                    }),
                });
            }
        });
    }
    return chartData;
}

console.log(JSON.stringify(getHighchartsData(), null, 2));
