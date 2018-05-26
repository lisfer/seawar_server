const FIELD = {EMPTY: 0, SHIP: 10, BORDER: 1, MAX_X: 10, MAX_Y: 10, HIT: 'hit', MISS: 'miss'};

let createField = (field) => {
    let cells = '<table>';
    for(let i = 0; i < 10; i++) {
        cells += '<tr>';
        for(let j = 0; j < 10; j++) {
            cells += '<td></td>';
        }
        cells += '</tr>';
    }
    cells += '</table>';
    console.log(field, cells);
    $(field).html(cells)
};

let setShips = (field, user) => {
    $.ajax({
        url: '/init_ship/' + (user ? 'user' : 'computer'),
        async: false,
        success: (data) => {
            let cells = field.find('td');
            for (i in data) {
                data[i] == FIELD.SHIP ? $(cells[i]).addClass('shipCell'): '';
                cells[i].x = i % FIELD.MAX_X;
                cells[i].y = Math.floor(i / FIELD.MAX_X);
            }
        }
    });
};

let allowShoots = (field) => {
    field.find('td').click((elem) => {
        let cell = elem.target;
        console.log(cell.x, cell.y);
        $.ajax({
            url: '/user_shoot',
            method: 'post',
            data: {x: cell.x, y: cell.y},
            success: (data) => {
                if (data == FIELD.HIT) {
                    $(cell).addClass('hit shooted');
                    $(cell).unbind('click')
                } else if (data == FIELD.MISS) {
                    $(cell).addClass('miss shooted');
                    $(cell).unbind('click')
                    computerShoot();
                } else {
                    console.log(data);
                }
            }
        })
    })
};

let computerShoot = () => {
    $.ajax({
        url: '/computer_shoot',
        method: 'post',
        async: false,
        success: (data) => {
            cellN = data.y * FIELD.MAX_X + data.x;
            $($('#fieldUser td')[cellN]).addClass(data.answer ? (computerShoot(), FIELD.HIT + ' shooted') : FIELD.MISS + ' shooted');
        }
    })
}

$(document).ready(() => {

    let userField = $('#fieldUser');
    createField(userField);
    setShips(userField, true);

    let compField = $('#fieldComp');
    createField(compField);
    setShips(compField);

    allowShoots(compField);

});