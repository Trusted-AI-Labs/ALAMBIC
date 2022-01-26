/**
 * Based on the demo of amCharts 5 for Multiple Value Axes
 */

function drawClassificationChart() {
    data = requestData('performance', 'classification');
    drawPerformanceChart(data, ['precision', 'recall', 'accuracy', 'mcc', 'f1_score']);
}

$(document).ready(function () {
    drawClassificationChart();
}