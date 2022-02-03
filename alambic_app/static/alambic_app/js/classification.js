/**
 * Based on the demo of amCharts 5 for Multiple Value Axes
 */

function drawClassificationChart() {
    var data;
    data = requestData('performance', 'classification');
    data.done(function (response) {
        drawPerformanceChart(response, ['precision', 'recall', 'accuracy', 'mcc', 'f1_score']);
    });
}

$(document).ready(function () {
    am5.ready(function () {
        drawClassificationChart();
    });
});