function requestData(reqData, type) {
    return $.ajax({
        type: "GET",
        url: "/data",
        data: {
            'data_type': type,
            'data': reqData
        },
        dataType: "json",
    });
}

function drawPerformanceChart(data, size, fields) {
    /**
     * Based on https://www.amcharts.com/demos/multiple-value-axes/#code and
     * https://jsfiddle.net/api/post/library/pure/
     */
    var root = am5.Root.new("plots_performance");
    root.setThemes(
        [
            am5themes_Animated.new(root)
        ]
    );
    var chart = root.container.children.push(
        am5xy.XYChart.new(root, {
            panX: false,
            panY: false,
            wheelX: "panX",
            wheelY: "zoomX",
            maxTooltipDistance: -1
        })
    );

    var cursor = chart.set("cursor", am5xy.XYCursor.new(root, {
        behavior: "zoomX"
    }));
    cursor.lineY.set("visible", false);

    var xAxis = chart.xAxes.push(
        am5xy.ValueAxis.new(root, {
                valueXField: "training_size",
                max: size,
                renderer: am5xy.AxisRendererX.new(root, {}),
                tooltip: am5.Tooltip.new(root, {})
            }
        )
    );

    var yAxis = chart.yAxes.push(am5xy.ValueAxis.new(root, {
        renderer: am5xy.AxisRendererY.new(root, {})
    }));

    fields.forEach(element => {
        addSeries(data, chart, root, element, "training_size", xAxis, yAxis)
    });


    var legend = chart.rightAxesContainer.children.push(
        am5.Legend.new(root, {
            width: 200,
            paddingLeft: 15,
            height: am5.percent(100)
        }));

    legend.itemContainers.template.events.on("pointerover", function (e) {
        var itemContainer = e.target;

        // As series list is data of a legend, dataContext is series
        var series = itemContainer.dataItem.dataContext;

        chart.series.each(function (chartSeries) {
            if (chartSeries != series) {
                chartSeries.strokes.template.setAll({
                    strokeOpacity: 0.15,
                    stroke: am5.color(0x000000)
                });
            } else {
                chartSeries.strokes.template.setAll({
                    strokeWidth: 3
                });
            }
        })
    })

    // When legend item container is unhovered, make all series as they are
    legend.itemContainers.template.events.on("pointerout", function (e) {
        var itemContainer = e.target;
        var series = itemContainer.dataItem.dataContext;

        chart.series.each(function (chartSeries) {
            chartSeries.strokes.template.setAll({
                strokeOpacity: 1,
                strokeWidth: 1,
                stroke: chartSeries.get("fill")
            });
        });
    })

    legend.itemContainers.template.set("width", am5.p100);
    legend.valueLabels.template.setAll({
        width: am5.p100,
        textAlign: "right"
    });

    // It's is important to set legend data after all the events are set on template, otherwise events won't be copied
    legend.data.setAll(chart.series.values);


    // Make stuff animate on load
    // https://www.amcharts.com/docs/v5/concepts/animations/
    chart.appear(1000, 100);
}

function addSeries(data, chart, root, yfield, xfield, xAxis, yAxis) {
    let nameY = yfield.charAt(0).toUpperCase() + yfield.slice(1);
    var series = chart.series.push(
        am5xy.LineSeries.new(root, {
            name: nameY,
            xAxis: xAxis,
            yAxis: yAxis,
            valueYField: yfield,
            valueXField: xfield,
            legendValueText: "{valueY}",
            tooltip: am5.Tooltip.new(root, {
                    pointerOrientation: "horizontal",
                    labelText: "[bold]{name}[/]:{valueY}"
                }
            )
            }
        )
    );
    series.data.setAll(data);
    series.appear();
}

