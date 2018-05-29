from flask import render_template, jsonify, session, request, g
from seawar_skeleton import SeaPlayground, SeaField, IncorrectCoordinate, ComputerPlayer, Cell, SIGNALS

from main import app


class SeaFieldJSON(SeaField):

    def to_json(self):
        return dict(x=self.max_x, y=self.max_y, data=[[cell.x, cell.y, cell.value] for cell in self._cells])

    def get_values_list(self):
        return [dict(x=cell.x, y=cell.y, value=cell.value) for cell in self._cells]

    def get_number_of_cells(self):
        return self.max_x * self.max_y

    @classmethod
    def from_json(cls, json_data):
        if json_data:
            field = cls(json_data['x'], json_data['y'])
            [field.set(x, y, v) for x, y, v in json_data['data']]
        else:
            field = cls()
        return field

    @classmethod
    def from_session(cls, name):
        g.to_session = g.to_session if g.get('to_session') else {}
        field = cls.from_json(session.get(name))
        g.to_session[name] = field
        return field


class ComputerPlayerJSON(ComputerPlayer, SeaFieldJSON):

    def to_json(self):
        return SeaFieldJSON.to_json(self.target_field)

    @classmethod
    def from_json(cls, json_data):
        if json_data:
            comp = cls(json_data['x'], json_data['y'])
            comp.target_field = SeaFieldJSON.from_json(json_data)
        else:
            comp = cls()
        return comp


@app.route('/api/docs')
def docs():
    print(app)



    return app.api_docs.html()

@app.route('/')
def index():
    session.clear()
    constants = dict(EMPTY=Cell.EMPTY, SHIP=Cell.SHIP, BORDER=Cell.BORDER, MAX_X=10, MAX_Y=10,
                     HIT=SIGNALS.HITTING, MISSED=SIGNALS.MISS, KILLED=SIGNALS.KILLED, WIN=SIGNALS.WIN)
    return render_template('index.html', constants=constants)


@app.route('/init_user_ship', methods=['POST'])
@app.api_docs.doc
def set_user_ships():
    """
    Init user Field. Randomly sets ships on it

    :return: List with values of Cells: (Cell.EMPTY or Cell.SHIP).
        Field is reduced to one list line by line: [(x=0, y=0), (x=1, y=0), (x=2, y=0),...(x=0, y=1), (x=1, y1=1), ..]
    """
    field = SeaFieldJSON()
    SeaPlayground.put_ships_random(field)
    session['user_field'] = field.to_json()
    return jsonify(field.get_values_list())


@app.route('/init_enemy_ship', methods=['POST'])
@app.api_docs.doc
def set_enemy_ships():
    """
       Init computer Field. Randomly sets ships on it

       :return: dict(cellsNumber = total number of cells on the field)
       """
    field = SeaFieldJSON()
    SeaPlayground.put_ships_random(field)
    session['computer_field'] = field.to_json()
    return jsonify(dict(cellsNumber=field.get_number_of_cells()))


@app.route('/user_shoot', methods=['POST'])
@app.api_docs.doc
def user_shoot():
    """
    Makes shoot to enemy field to specified coordinates

    :api_param x: x part of cell-coordinate
    :api_param y: y part of cell-coordinate
    :return: dict(
        shoot => Result of the shoot (
            HIT=SIGNALS.HITTING, MISSED=SIGNALS.MISS, KILLED=SIGNALS.KILLED, WIN=SIGNALS.WIN)
        cells => List of cells of the killed ship (if it was killed) otherwise - cells where shoot was made
        border => List of border cells for the ship (if the ship was killed)
    """
    field = SeaFieldJSON.from_session('computer_field')

    try:
        x, y = (lambda x, y: (int(x), int(y)))(*request.form.values())
        resp = SeaPlayground.income_shoot_to(field, x, y)
    except IncorrectCoordinate as e:
        return str(e)
    except (ValueError, TypeError):
        return f'Invalid coordinates {x} : {y}'

    border = (field._find_border_cells(*field.find_ship_vector(resp['cells']))
              if resp['signal'] == SIGNALS.KILLED else [])
    resp = dict(shoot=resp['signal'], border=border)

    return jsonify(resp)


@app.route('/computer_shoot', methods=['POST'])
@app.api_docs.doc
def computer_shoot():
    """
    Request for computer shoot. Updates field of the player on server side

    :return: dict(
        shoot => Result of the shoot (
            HIT=SIGNALS.HITTING, MISSED=SIGNALS.MISS, KILLED=SIGNALS.KILLED, WIN=SIGNALS.WIN)
        cells => List of cells of the killed ship (if it was killed) otherwise - cells where shoot was made
        border => List of border cells for the ship (if the ship was killed)
    """
    computer_player = ComputerPlayerJSON.from_session('computer_targets')
    user_field = SeaFieldJSON.from_session('user_field')
    resp = SeaPlayground.make_shoot_by_computer(computer_player, user_field)

    border = (user_field._find_border_cells(*user_field.find_ship_vector(resp['cells']))
              if resp['signal'] == SIGNALS.KILLED else [])
    resp = dict(shoot=resp['signal'], border=border, cells=resp['cells'])

    return jsonify(resp)


@app.after_request
def save_session(response):
    if g.get('to_session'):
        for name, obj in g.to_session.items():
            session[name] = obj.to_json()
    return response
