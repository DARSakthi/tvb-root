/**
 * TheVirtualBrain-Framework Package. This package holds all Data Management, and 
 * Web-UI helpful to run brain-simulations. To use it, you also need do download
 * TheVirtualBrain-Scientific Package (for simulators). See content of the
 * documentation-folder for more details. See also http://www.thevirtualbrain.org
 *
 * (c) 2012-2013, Baycrest Centre for Geriatric Care ("Baycrest")
 *
 * This program is free software; you can redistribute it and/or modify it under 
 * the terms of the GNU General Public License version 2 as published by the Free
 * Software Foundation. This program is distributed in the hope that it will be
 * useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
 * License for more details. You should have received a copy of the GNU General 
 * Public License along with this program; if not, you can download it here
 * http://www.gnu.org/licenses/old-licenses/gpl-2.0
 *
 **/

/*
 * This file handles the display and functionality of the 2d table view
 */
/*
 * Used to keep track of the start and end point for each quadrant.
 */
var startPointsX = [];
var endPointsX = [];
var startPointsY = [];
var endPointsY = [];

/*
 * Keep references to the last edited element, element color, and element class.
 * To be used for switching back to the original after an edit is performed.
 */
var lastEditedElement = null;
var lastElementColor = null;
var lastElementClass = null;

/**
 * Get the position of a element in the page. Used when finding out the position where the 
 * menu with information about a specific edge should be displayed.
 * 
 * @param elem - the element for which you want the absolute position in the page
 * 
 * @return a dictionary of the form {x: 'value of x offset', y: 'value of y offset'}
 */
function getMenuPosition(elem, contextMenuDiv){  
   
    var posX = 210;  // Default offset
    var posY = 15;

    while(elem != null){
        posX += elem.offsetLeft;
        posY += elem.offsetTop;
        elem = elem.offsetParent;
    }
    var $w = $("#scrollable-matrix-section");
    posY -= $w.scrollTop();
    if ($w[0].offsetTop > 0) {
        posY -= $w[0].offsetTop;
        posY -= ($("#main").scrollTop() - $w[0].offsetTop);
    }
    //posX -= $w.scrollLeft()

    var mh = 214; //$(contextMenuDiv).height();
    var mw = 200; //$(contextMenuDiv).width()
    var ww = $("body").width() - 15;
    var wh = Math.max($(window).height(), $w.height());

    var maxRight = posX;
    if (maxRight > ww) {
        posX -= (maxRight - ww);
    }

    var dir = "down";
    if (posY + mh > wh) {
        dir = "up";
    }
    if (dir == "up") {
        posY -= (mh + 25);
    }
    return {x : posX, y : posY };
} 

/**
 * Method called on the click event of a table box that represents a certain node from the connectivity matrix
 *
 * @param table_elem the dom element which fired the click event
 */
function changeSingleCell(table_elem, i, j) {

    var inputDiv = document.getElementById('editNodeValues');
    if (!(GFUNC_isNodeAddedToInterestArea(i) && GFUNC_isNodeAddedToInterestArea(j))) {
        displayMessage("The node you selected is not in the current interest area!", "warningMessage");
    }
    if (inputDiv.style.display == 'none') {
        inputDiv.style.display = 'block';
    } else {
        lastEditedElement.className = lastElementClass;
    }
    lastEditedElement = table_elem;
    lastElementClass = table_elem.className;
    table_elem.className = "node edited";
    var element_position = getMenuPosition(table_elem, inputDiv);
    inputDiv.style.position = 'fixed';
    inputDiv.style.left = element_position.x + 'px';
    inputDiv.style.top = element_position.y + 'px';

    var labelInfoSource = document.getElementById('selectedSourceNodeDetails');
    var labelInfoTarget = document.getElementById('selectedTargetNodeDetails');
    var descriptionText = GVAR_pointsLabels[i];
    if (labelInfoSource != null) {
        labelInfoSource.innerHTML = descriptionText;
    }
    descriptionText = GVAR_pointsLabels[j];
    if (labelInfoTarget != null) {
        labelInfoTarget.innerHTML = descriptionText;
    }

    var inputText = document.getElementById('weightsValue');
    inputText.value = GVAR_interestAreaVariables[GVAR_selectedAreaType]['values'][i][j];

    var hiddenNodeField = document.getElementById('currentlyEditedNode');
    hiddenNodeField.value = table_elem.id;
    MATRIX_colorTable();
}


/**
 * Method called when the 'Save' button from the context menu is pressed.
 * If a valid float is recieverm store the value in the weights matrix and if not
 * display an error message. Either way close the details context menu.
 */
function saveNodeDetails() {
    var inputText = document.getElementById('weightsValue');
    var newValue = parseFloat($.trim(inputText.value));
    var hiddenNodeField = document.getElementById('currentlyEditedNode');
    var tableNodeID = hiddenNodeField.value;
    var table_element = document.getElementById(tableNodeID);
    table_element.className = lastElementClass;

    if (isNaN(newValue)) {
        displayMessage('The value you entered is not a valid float. Original value is kept.', 'warningMessage');
    } else {
        //displayMessage('')
        var selectedMatrix = GVAR_interestAreaVariables[GVAR_selectedAreaType];
        var indexes = tableNodeID.split("td_" + selectedMatrix.prefix + '_')[1].split("_");
        var idx = indexes[0];
        var jdx = indexes[1];

        if (newValue > selectedMatrix.max_val){
            selectedMatrix.max_val = newValue;
            CONN_initLinesHistorgram();
        }
        if (newValue < 0) {
            newValue = 0;
        }
        if (newValue < selectedMatrix.min_val){
            selectedMatrix.min_val = newValue;
            CONN_initLinesHistorgram();
        }
        if (selectedMatrix.values[idx][jdx] == selectedMatrix.max_val) {
            selectedMatrix.values[idx][jdx] = newValue;
            selectedMatrix.max_val = 0;
            for (var i=0; i<selectedMatrix.values.length; i++) {
                for (var j=0; j<selectedMatrix.values.length; j++) {
                    if (selectedMatrix.values[i][j] > selectedMatrix.max_val) {
                        selectedMatrix.max_val = selectedMatrix.values[i][j];
                    }
                }
            }
            CONN_initLinesHistorgram();
        }
        else {
            if (selectedMatrix.values[idx][jdx] == 0 && newValue > 0) {
                CONN_comingInLinesIndices[jdx].push(parseInt(idx));
                CONN_comingOutLinesIndices[idx].push(parseInt(jdx));
            }
            if (selectedMatrix.values[idx][jdx] > 0 && newValue == 0) {
                HLPR_removeByElement(CONN_comingInLinesIndices[jdx], parseInt(idx));
                HLPR_removeByElement(CONN_comingOutLinesIndices[idx], parseInt(jdx));
            }
            selectedMatrix.values[idx][jdx] = newValue;
            CONN_lineWidthsBins[idx][jdx] = CONN_getLineWidthValue(newValue);
        }
    }
    var inputDiv = document.getElementById('editNodeValues');
    inputDiv.style.display = 'none';
    lastElementClass = null;
    lastEditedElement = null;
    lastElementColor = null;

    MATRIX_colorTable();
    GFUNC_updateLeftSideVisualization();
}


/**
 * Hide the details context menu that pops up aside a edited element. This
 * method is called when pressing the 'Cancel' button or when clicking outside the table/canvas.
 */
function hideNodeDetails() {
    var inputDiv = document.getElementById('editNodeValues');
    var hiddenNodeField = document.getElementById('currentlyEditedNode');
    var tableNodeID = hiddenNodeField.value;
    if (tableNodeID != null && tableNodeID != "") {
        inputDiv.style.display = 'none';
        if (lastEditedElement != null) {
            lastEditedElement.className = lastElementClass;
            lastEditedElement.style.backgroundColor = lastElementColor;
        }
        hiddenNodeField.value = null;
        lastElementClass = null;
        lastEditedElement = null;
        lastElementColor = null;
        MATRIX_colorTable();
    }
}

/**
 * Method used to toggle between show/hide in-going lines. Used from the details context menu 
 * aside a edited element.
 * 
 * @param index - specified which of the two nodes is the one for which to make the toggle,
 * 				  0 = source node, 1 = destination node
 */
function toggleIngoingLines(index) {
    var values = GVAR_interestAreaVariables[GVAR_selectedAreaType].values;
    var prefix = GVAR_interestAreaVariables[GVAR_selectedAreaType].prefix;

    var hiddenNodeField = document.getElementById('currentlyEditedNode');
    var indexes = hiddenNodeField.value.split("td_" + prefix + '_')[1].split("_");
    var idx = indexes[index];

    for (var i=0; i < NO_POSITIONS; i++) {
        if (values[i][indexes[index]] > 0) {
            if (GVAR_connectivityMatrix[i][idx] === 1) {
                GVAR_connectivityMatrix[i][idx] = 0;
            } else {
                GVAR_connectivityMatrix[i][idx] = 1;
            }
        } else {
            GVAR_connectivityMatrix[i][idx] = 0;
        }
    }
    GFUNC_updateLeftSideVisualization();
}

/**
 * Method used to toggle between show/hide outgoing lines. Used from the details context menu 
 * aside a edited element.
 * 
 * @param index - specified which of the two nodes is the one for which to make the toggle,
 * 				  0 = source node, 1 = destination node
 */
function toggleOutgoingLines(index) {
    var values = GVAR_interestAreaVariables[GVAR_selectedAreaType].values;
    var prefix = GVAR_interestAreaVariables[GVAR_selectedAreaType].prefix;

    var hiddenNodeField = document.getElementById('currentlyEditedNode');
    var indexes = hiddenNodeField.value.split("td_" + prefix + '_')[1].split("_");
    var idx = indexes[index];

    for (var i=0; i<NO_POSITIONS; i++) {
        if (values[idx][i] > 0 ) {
            if (GVAR_connectivityMatrix[idx][i] === 1) {
                GVAR_connectivityMatrix[idx][i] = 0;
            } else {
                GVAR_connectivityMatrix[idx][i] = 1;
            }
        } else {
            GVAR_connectivityMatrix[idx][i] = 0;
        }
    }
    GFUNC_updateLeftSideVisualization();
}

/**
 * Method used to cut ingoing lines. Used from the details context menu 
 * aside a edited element.
 * 
 * @param index - specified which of the two nodes is the one for which to make the cut,
 *                0 = source node, 1 = destination node
 */
function cutIngoingLines(index) {
    var values = GVAR_interestAreaVariables[GVAR_selectedAreaType].values;
    var prefix = GVAR_interestAreaVariables[GVAR_selectedAreaType].prefix;

    var hiddenNodeField = document.getElementById('currentlyEditedNode');
    var indexes = hiddenNodeField.value.split("td_" + prefix + '_')[1].split("_");
    var idx = indexes[index];
    var i;

    for (i=0; i<NO_POSITIONS; i++) {
        GVAR_connectivityMatrix[i][idx] = 0;
    }
    for (i=0; i<NO_POSITIONS; i++) {
        if (values[i][idx] > 0){
            HLPR_removeByElement(CONN_comingInLinesIndices[idx], parseInt(i));
            HLPR_removeByElement(CONN_comingOutLinesIndices[i], parseInt(idx));
        }
        values[i][idx] = 0;
    }
    MATRIX_colorTable();
    GFUNC_updateLeftSideVisualization();
}

/**
 * Method used to cut outgoing lines. Used from the details context menu 
 * aside a edited element.
 * 
 * @param index - specified which of the two nodes is the one for which to make the cut,
 * 				  0 = source node, 1 = destination node
 */
function cutOutgoingLines(index) {
    var values = GVAR_interestAreaVariables[GVAR_selectedAreaType].values;
    var prefix = GVAR_interestAreaVariables[GVAR_selectedAreaType].prefix;

    var hiddenNodeField = document.getElementById('currentlyEditedNode');
    var indexes = hiddenNodeField.value.split("td_" + prefix + '_')[1].split("_");
    var idx = indexes[index];

    for (var i=0; i<NO_POSITIONS; i++) {
        if (values[idx][i] > 0){
            HLPR_removeByElement(CONN_comingInLinesIndices[i], parseInt(idx));
            HLPR_removeByElement(CONN_comingOutLinesIndices[idx], parseInt(i));
        }
        GVAR_connectivityMatrix[idx][i] = 0;
        values[idx][i] = 0;
    }	
    MATRIX_colorTable();
    GFUNC_updateLeftSideVisualization();
}



function refreshTableInterestArea() {
    if ($('#div-matrix-tracts').length > 0) {
        for (var i = 0; i < NO_POSITIONS; i++) {
            updateNodeInterest(i);
        }
    }
}

/**
 * For a given node index update the style of the table correspondingly.
 */
function updateNodeInterest(nodeIdx) {
    var isInInterest = GFUNC_isNodeAddedToInterestArea(nodeIdx);
    // todo: these two queries are very expensive on the big dom that we have. This function is called for each node. 400ms
    // construct the id's and select by id
    var upperSideButtons = $("th[id^='upper_change_" + nodeIdx + "_']");
    var leftSideButtons = $("td[id^='left_change_" + nodeIdx + "_']");

    var prefix = GVAR_interestAreaVariables[GVAR_selectedAreaType].prefix;

    for (var k = 0; k < upperSideButtons.length; k++) {
        if (isInInterest) {
            upperSideButtons[k].className = 'selected';
        } else {
            upperSideButtons[k].className = '';
        }
    }
    
    for (var k = 0; k < leftSideButtons.length; k++) {
        if (isInInterest) {
            leftSideButtons[k].className = 'identifier selected';
        } else {
            leftSideButtons[k].className = 'identifier';
        }
    }    
    
    for (var i=0; i<NO_POSITIONS; i++){	
        var horiz_table_data_id = 'td_' + prefix + '_' + nodeIdx + '_' + i;
        var vertical_table_data_id = 'td_' + prefix + '_' + i + '_' + nodeIdx;
        var horiz_table_element = document.getElementById(horiz_table_data_id);
        var vertical_table_element = document.getElementById(vertical_table_data_id);

        if (isInInterest && GFUNC_isNodeAddedToInterestArea(i)) {
            vertical_table_element.className = 'node selected';
            horiz_table_element.className = 'node selected';
        }
        else {
            vertical_table_element.className = 'node';
            horiz_table_element.className = 'node';
        }
    }
}

function _toggleNode(index){
    GFUNC_toggleNodeInInterestArea(index);
    updateNodeInterest(index);
    GFUN_updateSelectionComponent();
}
/**
 * Method called when clicking on a node index from the top column. Change the entire column
 * associated with that index
 *
 * @param domElem the dom element which fired the click event
 */  
function changeEntireColumn(domElem) {
    var index = domElem.id.split("upper_change_")[1];
    index = parseInt(index.split('_')[0]);
    _toggleNode(index);
}


/**
 * Method called when clicking on a node label from the left column. Change the entire row
 * associated with that index
 *
 * @param domElem the dom element which fired the click event
 */  
function changeEntireRow(domElem) {
    var index = domElem.id.split("left_change_")[1];
    index = parseInt(index.split('_')[0]);
    _toggleNode(index);
}


/**
 * Helper methods that store information used when the colorTable method is called
 */

function TBL_storeHemisphereDetails(newStartPointsX, newEndPointsX, newStartPointsY, newEndPointsY) {
    startPointsX = eval(newStartPointsX);
    endPointsX = eval(newEndPointsX);
    startPointsY = eval(newStartPointsY);
    endPointsY = eval(newEndPointsY);
}

/**
 * Function to update the legend colors; the gradient will be created only after the table was drawn
 * so it will have the same size as the table matrix
 * @private
 */
function _updateLegendColors(){
    var div_id = GVAR_interestAreaVariables[GVAR_selectedAreaType]['legend_div_id'];
    var legendDiv = document.getElementById(div_id);

    var height = Math.max($("#div-matrix-weights")[0].clientHeight, $("#div-matrix-tracts")[0].clientHeight);
    ColSch_updateLegendColors(legendDiv, height);

    ColSch_updateLegendLabels('#table-' + div_id, GVAR_interestAreaVariables[GVAR_selectedAreaType]['min_val'],
                              GVAR_interestAreaVariables[GVAR_selectedAreaType]['max_val'], height);
}


/**
 * Method that colors the entire table.
 */
function MATRIX_colorTable() {
    var selectedMatrix = GVAR_interestAreaVariables[GVAR_selectedAreaType];
    var prefix_id = selectedMatrix.prefix;
    var dataValues = selectedMatrix.values;
    var minValue = selectedMatrix.min_val;
    var maxValue = selectedMatrix.max_val;

    for (var hemisphereIdx=0; hemisphereIdx<startPointsX.length; hemisphereIdx++){
        var startX = startPointsX[hemisphereIdx];
        var endX = endPointsX[hemisphereIdx];
        var startY = startPointsY[hemisphereIdx];
        var endY = endPointsY[hemisphereIdx];

        for (var i=startX; i<endX; i++){
            for (var j=startY; j<endY; j++) {
                var tableDataID = 'td_' + prefix_id + '_' + i + '_' + j;
                var tableElement = document.getElementById(tableDataID);
                if (dataValues){
                    tableElement.style.backgroundColor = getGradientColorString(dataValues[i][j], minValue, maxValue);
                }
            }
        }
    }
    _updateLegendColors();
}

function saveChanges() {
    // clone the weights matrix
    $("#newWeightsId").val($.toJSON(GVAR_interestAreaVariables[1]['values']));
    $("#newTractsId").val($.toJSON(GVAR_interestAreaVariables[2]['values']));
    $("#interestAreaNodeIndexesId").val($.toJSON(GVAR_interestAreaNodeIndexes));
    $("#experimentFormId").submit();
}



