const CELL = {EMPTY: 0, SHIP: 10, BORDER: 1};


let createField = (field) => {
    let cells = '<table>';
    for(let i = 0; i < 10; i++) {
        cells += '<tr>';
        for(let j = 0; j < 10; j++) {
            cells += '<td></td>';
        }
        cells += '</tr>';
    }
    cells += '<table>';
    console.log(field, cells);
    $(field).html(cells)
};

let setShips = (field) => {
    $.ajax({
        url: '/set_all_ships_random',
        success: (data) => {
            let cells = field.find('td');
            for (i in data) {
                data[i] == CELL.SHIP ? $(cells[i]).addClass('shipCell'): '';
            }
        }
    });
};


$(document).ready(() => {


    let mainField = $('#field');
    createField(mainField);
    setShips(mainField);

});