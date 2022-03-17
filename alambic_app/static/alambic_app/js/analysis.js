/**
 * Based on the demo of amCharts 5 for Multiple Value Axes
 */

function drawAnalysisChart() {
    var data;
    data = requestData('analysis', 'None');
    data.done(function (response) {
        drawPerformanceChart(response.data, response.size, response.strategies);
    });
}

$(document).ready(function () {
    am5.ready(function () {
        drawAnalysisChart();
    });
});