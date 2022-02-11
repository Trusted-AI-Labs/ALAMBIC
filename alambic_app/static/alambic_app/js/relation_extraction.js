/**
 * Inspired by the web tool UBIAI https://ubiai.tools/ + css
 */

var lastIdRelation = 0;
var colorMatching = {
    entities: {},
    relations: {}
};
var relationRecord = {};

//UTILS


/**
 * Based on the post https://martin.ankerl.com/2009/12/09/how-to-create-random-colors-programmatically/
 * @returns {string}
 */
function generateRandomColour() {
    function hsvToRGB(h, s, v) {
        var hI = Math.floor(h * 6);
        var f = h * 6 - hI;
        var p = v * (1 - s);
        var q = v * (1 - f * s);
        var t = v * (1 - (1 - f) * s);
        switch (hI) {
            case 0:
                var r = v;
                var g = t;
                var b = p;
                break;
            case 1:
                var r = q;
                var g = v;
                var b = p;
                break;
            case 2:
                var r = p;
                var g = v;
                var b = t;
                break;
            case 3:
                var r = p;
                var g = q;
                var b = v;
                break;
            case 4:
                var r = t;
                var g = p;
                var b = v;
                break;
            case 5:
                var r = v;
                var g = p;
                var b = q;
                break;
        }
        return [r, g, b];
    }

    let h = Math.random()
    let golden_ratio_conjugate = 0.618033988749895;
    h = h + golden_ratio_conjugate;
    h %= 1;
    let array = hsvToRGB(h, 0.5, 0.95)
    return 'rgb(' + array[0].toString(10) + ',' + array[1].toString(10) + ',' + array[2].toString(10) + ')'
}


function repositionLines() {
    for (const [key, value] of Object.entries(relationRecord)) {
        let line = value[0];
        let start = document.getElementById(line.start.id);
        let end = document.getElementById(line.end.id);
        let color = line.color;
        let text = value[1];
        relationRecord[key] = [getRemovableLine(start, end, text, color), text];
        line.remove();
    }
}


function removeEntity() {
    var content = $(this)[0].parentNode;
    var idEntity = content.id.replace('mark-', '')
    var div = content.parentNode;
    while ((content.firstChild) && (content.firstChild != $(this)[0])) {
        div.insertBefore(content.firstChild, content);
    }
    content.remove();

    var toDelete = [];

    // remove line
    for (const [key, value] of Object.entries(relationRecord)) {
        var array = key.split(',');
        if ((array[0] == idEntity) || (array[1] == idEntity)) {
            toDelete.push(key);
            value[0].remove();
        }
    }

    toDelete.forEach(key => {
        delete relationRecord[key];
    });
    repositionLines();
}


function selectEntity() {
    var object = $(this)[0];
    if (object.classList.contains('preselected')) {
        object.classList.remove('preselected')
    } else {
        object.classList.add('preselected')
    }
}


function createButton(textButton, colorButton) {
    var buttonID = textButton + "-button";
    return `<button type="button" class="btn btn-primary" style="background-color:` + colorButton + `;border-color:` + colorButton + `" id="` + buttonID + `">` + textButton + `</button>`;
}

// INITIALIZATION
function initializeEntities(divSelectorID) {
    var data = requestData('model', 'EntityType');
    data.done(function (response) {
        response.forEach(element => {
            var button = createButton(element['name'], element['color']);
            colorMatching.entities[element['color']] = element['name'];
            $(button).appendTo($(divSelectorID));
            $(divSelectorID).append(' ');
            document.getElementById(element['name'] + "-button").addEventListener('click', tagEntity, false)
        });
    })
}

function initializeRelations(divSelectorID) {
    var data = requestData('model', 'RelationType');
    data.done(function (response) {
        response.forEach(element => {
            var button = createButton(element['name'], element['color']);
            colorMatching.relations[element['color']] = element['name'];
            $(button).appendTo($(divSelectorID))
            document.getElementById(element['name'] + "-button").addEventListener('click', tagRelation, false)
            $(divSelectorID).append(' ');
        });
    });
}

function addEntity() {
    // Form to create new entity, will call also the button create
}

function addRelation() {
    // Form to create a new relation
}


// ELEMENTS TEXT MINING


/**
 * Found for the issue : https://github.com/anseki/leader-line/issues/70
 * Line that can be deleted and change color on hover
 */
function getRemovableLine(start, end, label, color) {
    var line = new LeaderLine(start, end, {
        size: 5,
        middleLabel: LeaderLine.pathLabel({
            text: label
        }),
        startSocket: 'top',
        endSocket: 'top',
        startPlug: 'disc',
        endPlug: 'disc',
        color: color,
        path: 'arc',
    });
    document.querySelector('.leader-line:last-of-type').addEventListener('dblclick', function () {
        let start = parseInt(line.start.id.replace("mark-", ""), 10);
        let end = parseInt(line.end.id.replace("mark-", ""), 10);
        delete relationRecord[[start, end]];
        line.remove();
    }, false);
    return line;
}

function tagEntity() {
    if ($(window.getSelection().anchorNode).closest("#text-div").attr("id") == "text-div") {
        var selObj = window.getSelection();
        if ((selObj.focusNode.parentNode.id == "text-div") | ((selObj.anchorNode.parentNode.id == "text-div"))) {
            return;
        }
        var idSpanStart = parseInt(selObj.anchorNode.parentNode.id, 10);
        var idSpanEnd = parseInt(selObj.focusNode.parentNode.id, 10);
        var focusNode = selObj.focusNode;
        var anchorNode = selObj.anchorNode;

        if (idSpanEnd < idSpanStart) {
            [idSpanStart, idSpanEnd, anchorNode, focusNode] = [idSpanEnd, idSpanStart, focusNode, anchorNode]; //if the selection was in the other direction
        }

        var tagSpanStart = `<span id="` + idSpanStart + `" class="card-body-span span-` + idSpanStart + `">`;
        var tagSpanEnd = `<span id="` + idSpanEnd + `" class="card-body-span span-` + idSpanEnd + `">` + focusNode.data + `</span>`;
        var startMark = `<mark id="mark-` + lastIdRelation + `" class="" style="background-color:` + $(this)[0].style['background-color'] + `;" data-toggle="tooltip" data-placement="bottom" title="` + $(this)[0].id.replace("-button", "") + `">` + tagSpanStart;
        var endMark = tagSpanEnd + `<span class="close mark-` + lastIdRelation + `">x</span></mark>`;


        var content = document.getElementById('text-div');
        content.innerHTML = content.innerHTML
            .replace(tagSpanStart, startMark)
            .replace(tagSpanEnd, endMark);


        // initialize button to close and selection for relation
        var list = document.getElementsByClassName("close");
        for (let element of list) {
            element.addEventListener('click', removeEntity, false);
        }
        var list = document.getElementsByTagName("MARK");
        for (let element of list) {
            element.addEventListener('click', selectEntity, false);
        }
        lastIdRelation += 1;
        repositionLines();
    }
}

function tagRelation() {
    var selection = document.getElementsByClassName("preselected");
    if (selection.length != 2) {
        alert("You need to select exactly two entities");
    } else {
        var idOne = parseInt(selection[0].id.replace('mark-', ''), 10);
        var idTwo = parseInt(selection[1].id.replace('mark-', ''), 10);
        var color = $(this)[0].style['background-color'];
        var text = $(this)[0].innerText;
        var line = getRemovableLine(selection[0], selection[1], text, color);

        relationRecord[[idOne, idTwo]] = [line, text];
    }
    // verifies that two entities are pre-selected (class mark)
    // and create a arrow line leader which can be double-clicked to disappear
}


$(document).ready(function () {
    initializeEntities("#entities");
    initializeRelations("#relation");
});