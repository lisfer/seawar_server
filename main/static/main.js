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
                if (data.shoot == FIELD.KILLED) {
                    let fieldCells = $('#fieldComp td');
                    for (let i in data.border) {
                        let cellN = data.border[i][1] * FIELD.MAX_X + data.border[i][0];
                        $(fieldCells[cellN]).addClass('border').unbind('click');
                    }
                }
                if (data.shoot === FIELD.HIT |  data.shoot === FIELD.KILLED) {
                    $(cell).addClass('hit');
                    $(cell).unbind('click')
                } else if (data.shoot === FIELD.MISSED) {
                    $(cell).addClass('miss');
                    $(cell).unbind('click');
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
            $($('#fieldUser td')[cellN]).addClass((data.shoot == FIELD.KILLED | data.shoot == FIELD.HIT) ? (computerShoot(), 'hit') : 'miss');
            if (data.shoot == FIELD.KILLED) {
                let fieldCells = $('#fieldUser td');
                for (let i in data.border) {
                    let cellN = data.border[i][1] * FIELD.MAX_X + data.border[i][0];
                    $(fieldCells[cellN]).addClass('border');
                }
            }
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