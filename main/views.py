from flask import render_template, jsonify, session, request, g
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

    @staticmethod
    def from_session(name):
        g.to_session = g.to_session if g.get('to_session') else {}
        field = SeaFieldJSON.from_json(session.get(name))
        g.to_session[name] = field
        return field


class SeaPlayground2(SeaPlayground):
    @staticmethod
    def make_shoot(target_field, enemy_field):
        x, y = SeaPlayground.find_target(target_field)
        answer = SeaPlayground.income_shoot(enemy_field, x, y)
        SeaPlayground.target_answer(target_field, x, y, answer)
        return x, y, answer


@app.route('/')
def index():
    session.clear()
    return render_template('index.html')


@app.route('/init_ship/<player>')
def set_all_ships_random(player):
    field = SeaFieldJSON()
    SeaPlayground.put_ships_random(field)
    session[f'{player}_field'] = field.to_json()
    return jsonify([cell.value for cell in field.cells])


@app.route('/user_shoot', methods=['POST'])
def user_shoot():
    field = SeaFieldJSON.from_session('computer_field')

    try:
        x, y = (lambda x, y: (int(x), int(y)))(*request.form.values())
        resp = 'hit' if SeaPlayground.income_shoot(field, x, y) else 'miss'
    except IncorrectCoordinate as e:
        return str(e)
    except (ValueError, TypeError):
        return f'Invalid coordinates {x} : {y}'

    session['computer_field'] = field.to_json()
    return resp


@app.route('/computer_shoot', methods=['POST'])
def computer_shoot():
    computer_targets = SeaFieldJSON.from_session('computer_targets')
    user_field = SeaFieldJSON.from_session('user_field')
    x, y, answer = SeaPlayground2.make_shoot(computer_targets, user_field)
    return jsonify(dict(x=x, y=y, answer=answer))


@app.after_request
def save_session(response):
    if g.get('to_session'):
        for name, obj in g.to_session.items():
            session[name] = obj.to_json()
    return response
