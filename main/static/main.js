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

let initUserShipsField = (field) => {
    createField(field);
    $.ajax({
        url: '/init_user_ship',
        method: 'post',
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

let initEnemyShipsField = (field, user) => {
    createField(field);
    $.ajax({
        url: '/init_enemy_ship',
        method: 'post',
        async: false,
        success: (data) => {
            let cells = field.find('td');
            for (let i = 0; i < data.cellsNumber; i ++) {
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
                let fieldCells = $('#fieldComp td');
                for (let i in data.border) {
                    let cellN = data.border[i][1] * FIELD.MAX_X + data.border[i][0];
                    $(fieldCells[cellN]).addClass('border').unbind('click');
                }
                if (data.shoot === FIELD.HIT |  data.shoot === FIELD.KILLED |  data.shoot === FIELD.WIN) {
                    $(cell).addClass('hit');
                    if (data.shoot === FIELD.WIN) {
                        return gameWin();
                    } else $(cell).unbind('click');
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

let gameWin = () => {
    $('#fieldComp td').unbind('click');
    $('#fieldComp').addClass('loser');
    $('#fieldUser').addClass('winner');
}

let gameLoose = () => {
    $('#fieldComp td').unbind('click');
    $('#fieldComp').addClass('winner');
    $('#fieldUser').addClass('loser');
}

let computerShoot = () => {
    $.ajax({
        url: '/computer_shoot',
        method: 'post',
        async: false,
        success: (data) => {
            let fieldCells = $('#fieldUser td');
            let hit = (data.shoot == FIELD.KILLED | data.shoot == FIELD.HIT);
            for (let i in data.cells) {
                cellN = data.cells[i][1] * FIELD.MAX_X + data.cells[i][0];
                $(fieldCells[cellN]).addClass(hit ?  'hit' : 'miss');
            }
            for (i in data.border) {
                let cellN = data.border[i][1] * FIELD.MAX_X + data.border[i][0];
                $(fieldCells[cellN]).addClass('border');
            }
            if (data.shoot == FIELD.WIN) return gameLoose();
            if (hit) computerShoot();
        }
    })
}

$(document).ready(() => {

    let userField = $('#fieldUser');
    initUserShipsField(userField);

    let compField = $('#fieldComp');
    initEnemyShipsField(compField);

    allowShoots(compField);

});