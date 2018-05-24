from flask import render_template, jsonify, session, request
from seawar_skeleton import SeaPlayground, Cell, I

from main import app


CELL_HIT = -10
CELL_MISSED = -1


class IncorectCoordinates(Exception):
    pass


class SeaPlaygroundJSON(SeaPlayground):

    def to_json(self):
        return [[cell.x, cell.y, cell.value] for cell in self.cells]

    def from_json(self, json_data):
        [self._field.set(x, y, v) for x, y, v in json_data]

    def income_shoot(self, x, y):
        if self._field.is_coord_correct(x, y):
            resp = CELL_HIT if self._field.get(x, y) == Cell.SHIP else CELL_MISSED
            self._field.set(x, y, resp)
            return resp == CELL_HIT
        raise IncorectCoordinates()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/init_ship/<player>')
def set_all_ships_random(player):
    s = SeaPlaygroundJSON(10, 10)
    for ship in [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]:
        s.put_ship_random(ship)
    session[f'{player}Ship'] = s.to_json()
    return jsonify([cell.value for cell in s.cells])


@app.route('/player_shoot', methods=['POST'])
def shoot():
    s = SeaPlaygroundJSON(10, 10)
    s.from_json(session['compShip'])
    try:
        x, y = (lambda x, y: (int(x), int(y)))(*request.form.values())
        resp = 'hit' if s.income_shoot(x, y) else 'miss'
    except (ValueError, TypeError, IncorectCoordinates):
        return f'Invalid coordinates {x} : {y}'

    session['compShip'] = s.to_json()
    return resp
