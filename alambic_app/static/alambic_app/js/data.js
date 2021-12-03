function LoadingFig(figure_name) {
    // console.log(figure_name);
    var table_row = `#${figure_name}`;
    // Make nested div
    var divID = figure_name + "_figure_div";
    // console.log(divID);
    $("<div></div>", {
        "id": divID,
        "class": "text-center"
    })
        .appendTo(table_row);

    var divSelector = `#${divID}`;
    // console.log(divSelector);

    $("<img>", {
        "class": "img-responsive loader-img mx-auto d-block pt-2",
        "src": ajaxLoaderPath,
        "alt": "Loading"
    }).appendTo(divSelector);

    $("<h4 class='loader-text mx-auto w-50'>Loading content.</h4>").appendTo(divSelector);

    return divSelector;
}


function drawTable(table_name) {

    var divSelector = LoadingFig(table_name);
    // console.log(divSelector);

    var dataRequest = requestData(table_name, 'table')
        .done(function (table_data) {
            console.log(table_name);

            var currentPage = window.location.pathname;
            var table;
            table = generateTable(table_name, table_data, divSelector);
        });

    return dataRequest;
}

function generateTable(name, data, divSelector) {

    //console.log(data);

    var tableId = name + "_table";
    $(divSelector).replaceWith(`<table id=${tableId} class='display'></table>`);
    var tableSelector = `#${tableId}`;

    var tableColumns = data.columns;
    var firstDataValue = data.data[0];

    console.log(data.columns);

    // Set renderer for list items
    tableColumns.forEach(col => {
        if (Array.isArray(firstDataValue[col.data])) {
            col.render = '[;\t ]';
        }
    });

    //console.log(tableColumns);


    // console.log(`Inserting table in ${tableSelector}`);

    insertHeaders(tableColumns, tableSelector);

    //Additional configuration options
    // data.responsive = true;
    data.autoWidth = false;
    data.pageLength = 25;


    return newTable;

}

function insertHeaders(columns, tableSelector) {

    // Add base header and footer to HTML table
    $('<thead><tr class="header-row-1"></tr></thead> <tfoot><tr></tr></tfoot>').appendTo(tableSelector);

    // If complex headers are defined special initialization is require, otherwise simply format and insert all columns
    columns.forEach(col => {

        // Add HTML tags and append to header
        $(`${tableSelector} tr`).append(`<th>${col}</th>`);
    });
    return false;
}


$(document).ready(function () {
    $(".table").each(function () {
        table_name = $(this).prop("id"); //id of a table div should correspond to the table name as accepted by server side handlers

        // $(`<h3> ${table_name} </h3>`).appendTo(this);
        var tableRequest = drawTable(table_name);
        tableRequests.push(tableRequest);
    });
});