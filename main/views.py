from flask import render_template, jsonify, session, request
from seawar_skeleton import SeaPlayground, SeaField, IncorrectCoordinate

from main import app


class SeaFieldJSON(SeaField):

    def to_json(self):
        return dict(x=self.max_x, y=self.max_y, data=[[cell.x, cell.y, cell.value] for cell in self.cells])

    @staticmethod
    def from_json(json_data):
        if json_data:
            field = SeaFieldJSON(json_data['x'], json_data['y'])
            [field.set(x, y, v) for x, y, v in json_data['data']]
        else:
            field = SeaFieldJSON()
        return field


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/init_ship/<player>')
def set_all_ships_random(player):
    field = SeaFieldJSON()
    SeaPlayground.put_ships_random(field)
    session[f'{player}_field'] = field.to_json()
    return jsonify([cell.value for cell in field.cells])


@app.route('/player_shoot', methods=['POST'])
def shoot():
    field = SeaFieldJSON.from_json(session['computer_field'])

    try:
        x, y = (lambda x, y: (int(x), int(y)))(*request.form.values())
        resp = 'hit' if SeaPlayground.income_shoot(field, x, y) else 'miss'
    except IncorrectCoordinate as e:
        return str(e)
    except (ValueError, TypeError):
        return f'Invalid coordinates {x} : {y}'

    session['computer_field'] = field.to_json()
    return resp
