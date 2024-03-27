var DIV="======================================";
var globalPropositions = [];

function mapLetterToIndex(letter) {
    letter = letter.toUpperCase();
    var index = letter.charCodeAt(0) - 'A'.charCodeAt(0);
    return index;
}

function format_logical_table(response, connI, connJ) {
    var tableHTML = '<table><thead><tr><th>P</th><th>Implies</th><th>Logical Relationship</th></tr></thead><tbody>';
    Object.keys(response.edges).forEach(function(key) {
          response.edges[key].forEach(function(prop) {
          tableHTML += '<tr><td>'
          tableHTML += key 
          tableHTML += '</td><td>' 
          tableHTML += '->' + prop
          tableHTML += '</td><td>'
          tableHTML += globalPropositions[connI][connJ][mapLetterToIndex(key)]
          tableHTML += '->'
          tableHTML += globalPropositions[connI][connJ][mapLetterToIndex(prop)]
          tableHTML += '</td></tr>'
   
        });
    });
    tableHTML += '</tbody></table>';
    return tableHTML;
}

function format_proposition_list(response) {

    var listItems = '';
    var propositions = []

    $.each(response, function(key, value) {
        console.log(DIV)
        console.log("VALUE")
        console.log(value)
        console.log(DIV)
        $.each(value, function(index, value) {
            if (typeof value === 'string') {
              console.log("Pushing", value)
              propositions.push(value)
              listItems += `<li>${value}</li>`;
            }
            console.log(DIV)
        });
        console.log(DIV)
        // manifest, printing out every proposition and returning a list of strings
        // reality, now i have printed out every proposition, returned list of strings, formatted the table, written a graph.png dir cleanup module that is called on index()
    });

    // Include the 'no-bullets' class in the <ul>
    console.log(propositions)
    var bulletList = `<ul class="no-bullets">${listItems}</ul>`;
    
    return {'propositions': propositions, 'bulletList': bulletList};
}

function cache_propositions(propositions, connI, connJ) {
    globalPropositions[connI][connJ]=propositions
    console.log("[ cache_propositions ] ", connI, " x ", connJ, " - ", globalPropositions[connI][connJ])
    return true
}

function parse_propositions(response, connI, connJ) {

    console.log(DIV);

    var p = format_proposition_list(response);
    var propositions = p.propositions;

    console.log("[ parse_propositions ] ", propositions)
    cache_propositions(propositions, connI, connJ)

    return propositions 
}

function adjustOpenDivs(divs) {
    const openDivs = document.querySelectorAll('.original_article:not(.minimized), .symbolic_logic:not(.minimized), .phrases_content:not(.minimized), .control_panel:not(.minimized), .graph_container:not(.minimized)');
    const numOpenDivs = openDivs.length;
    const gapSize = 8; 
    const totalGapSize = gapSize * (numOpenDivs - 1); 
    const containerWidth = document.querySelector('.container').offsetWidth; 
    const flexBasisPerDiv = (containerWidth - totalGapSize) / numOpenDivs / containerWidth * 100; 

    divs.forEach(div => {
      if (!div.classList.contains('minimized')) {
        div.style.flex = `1 1 ${flexBasisPerDiv}%`;
      } 
      else {
        div.style.flex = '0 1 10%'; 
      }
    });
}


function format_propositions(response, connI, connJ) {

    console.log(DIV);

    var p = format_proposition_list(response);
    var bulletList = p.bulletList;
    var propositions = p.propositions;
    var allEmpty = Object.values(response.edges).every(list => list.length === 0);
    if (allEmpty) {
        console.log("No node edges found.");
        var tableHTML = ''
    }
    else {
      var tableHTML = format_logical_table(response, connI, connJ);
    };

    //for (var key in response) {
    //  console.log(key);
    //}
    
    //var combinedList = response.conn_i.concat(response.conn_j);
    //console.log(combinedList);
    //var parts = prop.split(' -> ');
    //var subject = parts[0].trim();
    //var predicate = parts[1].trim();


    console.log(bulletList)
    return {
        tableHTML: tableHTML,
        bulletList: bulletList,
        propositions: propositions,
    };
}

document.addEventListener('DOMContentLoaded', function() {
    const divs = document.querySelectorAll('.original_article, .symbolic_logic, .phrases_content, .control_panel, .graph_container');
  // Add click event listener to each div
    divs.forEach(div => {
      div.addEventListener('click', function() {
        // Toggle the 'minimized' class on click
        this.classList.toggle('minimized');
      });
    });

    const minimizeButtons = document.querySelectorAll('.minimize-button');

    minimizeButtons.forEach(button => {
      button.addEventListener('click', function() {
        this.parentElement.classList.toggle('minimized');
        //adjustOpenDivs(divs);
      });
    });


    const connectionCells = document.querySelectorAll('.connection-cell');

    $('.connection-cell').click(function() {
        console.log($(this).data('conn-i') + ',' + $(this).data('conn-j'));
    });

    connectionCells.forEach(cell => {
        cell.addEventListener('click', function() {
            document.querySelectorAll('.highlight').forEach(el => {
                el.classList.remove('highlight');
            });

            const connI = cell.getAttribute('data-conn-i');
            const connJ = cell.getAttribute('data-conn-j');
            var $nextTd = $(this).next();

            document.getElementById(`${connI}`).classList.add('highlight');
            document.getElementById(`${connJ}`).classList.add('highlight');

            $.ajax({
                url: '/extract-propositions',  // Flask route
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({conn_i: connI, conn_j: connJ}),
                dataType: 'json',
                success: function(response) {
                    console.log(`Extracting propositions from ${connI}`);
                    console.log(`Extracting propositions from ${connJ}`);
                    console.log(response);
                    if (!globalPropositions.hasOwnProperty(connI)) {
                        globalPropositions[connI] = {};
                        if (!globalPropositions[connI].hasOwnProperty(connJ)) {
                            globalPropositions[connI][connJ] = {};
                        }
                    }
                    var propositions = parse_propositions(response, connI, connJ)
                    var htmlContent = format_propositions(response, connI, connJ)

                    var bulletList = htmlContent.bulletList
                    var propTable = htmlContent.tableHTML

                    globalPropositions[connI][connJ] = propositions;
                    console.log(propositions);
                    var elementDescription = `Clicked TD: Data-conn-i: ${connI}, Data-conn-j: ${connJ}, globalPropositions: ${globalPropositions[connI][connJ]}`;
                    alert(elementDescription);  // or console.log(elementDescription);
                    $nextTd.html('<div class="bullet-list">' + bulletList + '</div>' + '<div class="prop-table">' + propTable + '</div>');

                },
                error: function(error) {
                    console.log('Error:', error);
                }
            });
        });
    });
});
