from flask import render_template, jsonify, session
from seawar_skeleton import SeaPlayground

from main import app


class SeaPlaygroundJSON(SeaPlayground):

    def to_json(self):
        return [[cell.x, cell.y, cell.value] for cell in self.cells]

    def from_json(self, json_data):
        [self._field.set(x, y, v) for x, y, v in json_data]


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
