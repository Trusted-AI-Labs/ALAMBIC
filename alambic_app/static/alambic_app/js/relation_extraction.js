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

function enableTooltips() {
    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    })
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
    $(content).tooltip('dispose');
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
        var addButton = `<button type="button" id="add_entity" class="btn btn-success btn-sm"><i class="material-icons">add</i></button>`;
        $(addButton).appendTo($(divSelectorID));
        document.getElementById('add_entity').addEventListener('click', addEntity, false)
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
        var addButton = `<button type="button" id="add_relation" class="btn btn-success btn-sm"><i class="material-icons">add</i></button>`;
        $(addButton).appendTo($(divSelectorID));
        document.getElementById('add_relation').addEventListener('click', addRelation, false)
    });
}

function addEntity() {
    var formDiv = document.getElementById('newentity_div').getElementsByClassName("modal-body")[0];
    var managerDiv = document.getElementById('newentity_div');
    $.getJSON("/tasting/add",
        {
            formType: 'EntityType'
        })
        .done(function (formData) {
            $(formDiv).html(formData.form_html);
            $(managerDiv).modal({show: true});

            $('#confirm_add_entity_button').click(function (e) {
                // Block default submit behaviour, serialize form data and POST to the form view
                e.preventDefault();

                var data = $(formDiv).find(':input').serialize();

                $(formDiv).empty();

                $.post("/tasting/add", data.concat("&formType=EntityType"))
                    .done(function (response) {

                        // Update div where form was rendered, disable create button and select created variant
                        if (response.success) {
                            var button = createButton(response['name'], reponse['color']);
                            var divSelectorID = $(this).parentNode[0]
                            $(button).before($(this))
                            $(divSelectorID).append(' ');
                            document.getElementById(response['name'] + "-button").addEventListener('click', tagEntity, false)
                        } else {
                            // Render form with errors when it was not validated by the server
                            $(formDiv).html(response.form_html);
                        }
                    })
                    .fail(function (response) {
                        alert('Something went wrong when creating this entity.');
                    });
            });
        });
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
        var startMark = `<mark id="mark-` + lastIdRelation + `" class="" style="background-color:`
            + $(this)[0].style['background-color'] + `;" data-toggle="tooltip" data-placement="bottom" title="`
            + $(this)[0].id.replace("-button", "") + `">`
            + tagSpanStart;
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
        enableTooltips();
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

        while (selection.length) selection[0].classList.remove('preselected');
    }
}

function formatAnnotation() {
    var entitites = document.getElementsByTagName("MARK");
    var formattedJson = {
        tokens: [],
        relations: []
    };
    var entitiesIndex = {};
    var index = 0;

    for (let entity of entitites) {
        let startindex = parseInt(entity.firstChild.id, 10);
        let endindex = 0;
        let label = entity.getAttribute('data-original-title');
        let text = "";
        let entityID = parseInt(entity.id.replace('mark-', ''));

        for (let span of entity.childNodes) {
            if (!span.classList.contains('close')) {
                endindex = parseInt(span.id, 10);
                text += span.innerText;
            }
        }

        formattedJson.tokens.push({
            start_token: startindex,
            end_token: endindex,
            content: text.slice(0, -1),
            EntityType: label
        });

        entitiesIndex[entityID] = index;
        index++;
    }

    for (const [key, value] of Object.entries(relationRecord)) {
        var array = key.split(',');
        var components = [];

        array.forEach(element => {
            components.push(entitiesIndex[parseInt(element, 10)])
        });

        formattedJson.relations.push({
            components: components,
            RelationType: value[1]
        });
    }

    return formattedJson;
}


$(document).ready(function () {
    initializeEntities("#entities");
    initializeRelations("#relation");
    document.getElementById('submit_annotation').addEventListener('click', formatAnnotation, false)
});