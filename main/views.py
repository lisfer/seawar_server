from flask import render_template, jsonify, session, request, g
from seawar_skeleton import SeaPlayground, SeaField, IncorrectCoordinate, ComputerPlayer, Cell

from main import app


class SeaFieldJSON(SeaField):

    def to_json(self):
        return dict(x=self.max_x, y=self.max_y, data=[[cell.x, cell.y, cell.value] for cell in self._cells])

    def get_values_list(self):
        return [cell.value for cell in self._cells]

    def get_number_of_cells(self):
        return self.max_x * self.max_y

    @staticmethod
    def from_json(json_data):
        if json_data:
            field = SeaFieldJSON(json_data['x'], json_data['y'])
            [field.set(x, y, v) for x, y, v in json_data['data']]
        else:
            field = SeaFieldJSON()
        return field

    @staticmethod
    def from_session(name):
        g.to_session = g.to_session if g.get('to_session') else {}
        field = SeaFieldJSON.from_json(session.get(name))
        g.to_session[name] = field
        return field


@app.route('/')
def index():
    session.clear()
    constants = dict(EMPTY=Cell.EMPTY, SHIP=Cell.SHIP, BORDER=Cell.BORDER, MAX_X=10, MAX_Y=10,
                     HIT=Cell.HIT, MISSED=Cell.MISSED, KILLED=Cell.KILLED)
    return render_template('index.html', constants=constants)


@app.route('/init_user_ship', methods=['POST'])
def set_user_ships():
    field = SeaFieldJSON()
    SeaPlayground.put_ships_random(field)
    session['user_field'] = field.to_json()
    return jsonify(field.get_values_list())


@app.route('/init_enemy_ship', methods=['POST'])
def set_enemy_ships():
    field = SeaFieldJSON()
    SeaPlayground.put_ships_random(field)
    session['computer_field'] = field.to_json()
    return jsonify(dict(cellsNumber=field.get_number_of_cells()))


@app.route('/user_shoot', methods=['POST'])
def user_shoot():
    field = SeaFieldJSON.from_session('computer_field')

    try:
        x, y = (lambda x, y: (int(x), int(y)))(*request.form.values())
        resp = SeaPlayground.income_shoot(field, x, y)
    except IncorrectCoordinate as e:
        return str(e)
    except (ValueError, TypeError):
        return f'Invalid coordinates {x} : {y}'

    if resp == Cell.KILLED:
        cells = SeaPlayground._find_ship_cells(field, x, y)
        border = SeaPlayground._find_border_cells(field, *SeaPlayground._find_ship_vector(cells))
        resp = dict(shoot=resp, border=border)
    else:
        resp = dict(shoot=resp)

    return jsonify(resp)


@app.route('/computer_shoot', methods=['POST'])
def computer_shoot():
    computer_targets = SeaFieldJSON.from_session('computer_targets')
    user_field = SeaFieldJSON.from_session('user_field')
    x, y, answer = ComputerPlayer.make_shoot(computer_targets, user_field)
    resp=dict(x=x, y=y, shoot=answer)
    if answer == Cell.KILLED:
        cells = SeaPlayground._find_ship_cells(user_field, x, y)
        border = SeaPlayground._find_border_cells(user_field, *SeaPlayground._find_ship_vector(cells))
        resp['border'] = border
    return jsonify(resp)


@app.after_request
def save_session(response):
    if g.get('to_session'):
        for name, obj in g.to_session.items():
            session[name] = obj.to_json()
    return response
