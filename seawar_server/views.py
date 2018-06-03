from collections import namedtuple

from flask import render_template, jsonify, session, request, g, Response
from seawar_core import Field, ShipService, CoordOutOfRange, TargetField

from seawar_server import app


SIGNALS = namedtuple('SIGNALS', ['MISS', 'HIT', 'KILLED', 'WIN'])('miss', 'hit', 'killed', 'win')


class FieldJSON(Field):

    @staticmethod
    def cell_to_json(cell):
        return (cell.x, cell.y, cell.value, cell.is_shooted)

    def to_json(self):
        return dict(
            max_x=self.max_x,
            max_y=self.max_y,
            cells=[*map(self.cell_to_json, self.cells)])

    def get_ships(self):
        return [(cell.x, cell.y) for cell in self.cells if cell.is_ship]

    @classmethod
    def from_json(cls, json_data):
        if json_data:
            field = cls(json_data['max_x'], json_data['max_y'])
            [field.set(*data) for data in json_data['cells']]
        else:
            field = cls()
        return field

    @classmethod
    def from_session(cls, name):
        g.to_session = g.to_session if g.get('to_session') else {}
        field = cls.from_json(session.get(name))
        g.to_session[name] = field
        return field


class TargetFieldJSON(TargetField, FieldJSON):

    @staticmethod
    def cell_to_json(cell):
        return (cell.x, cell.y, cell.value)


def make_shoot(user_field, x, y):
    hit = ShipService.shoot_to(user_field, x, y)

    if hit:
        response = ShipService.get_ship_if_killed(user_field, x, y)
        signal = response and (
            SIGNALS.WIN if ShipService.is_fleet_killed(user_field) else SIGNALS.KILLED) or SIGNALS.HIT
    else:
        signal, response = SIGNALS.MISS, {}

    response.update(dict(signal=signal, x=x, y=y))
    return hit, response


@app.route('/api/docs')
def docs():
    return app.api_docs.html()


@app.route('/')
def index():
    session.clear()
    return render_template('index.html', constants={})


@app.route('/api/init_user_ship', methods=['POST'])
@app.api_docs.doc
def set_user_ships():
    """
    Init user Field. Randomly sets ships on it

    :return:
        {
            "max_x": <int> - width of the field
            "max_y": <int> - heigth of the field
            "cells": <List(Tuple(int, int)))> - list of cells that contain ships
         }
    """
    field = FieldJSON()
    ShipService.put_ships_random(field)
    session['user_field'] = field.to_json()
    return jsonify({'max_x': field.max_x, 'max_y': field.max_y, 'ships': field.get_ships()})


@app.route('/api/init_enemy_ship', methods=['POST'])
@app.api_docs.doc
def set_enemy_ships():
    """
       Init computer Field. Randomly sets ships on it

       :return:
           {
               :"max_x" <int>: width of the field
               :"max_y" <int>: height of the field
            }
       """
    field = FieldJSON()
    ShipService.put_ships_random(field)
    session['computer_field'] = field.to_json()
    session.pop('computer_targets', None)           # cleaning targets field too
    return jsonify({'max_x': field.max_x, 'max_y': field.max_y})


@app.route('/api/user_shoot', methods=['POST'])
@app.api_docs.doc
def user_shoot():
    """
    Makes shoot to enemy field to specified coordinates

    :api_param x: x part of cell-coordinate
    :api_param y: y part of cell-coordinate
    :return:
        {
            :"signal" <str>: 'missed' / 'hit' / 'killed' / 'win'
            :"ships" <list>: [[x, y], ...] or [] - list of cells that belongs to killed ship (if it was killed)
            :"boders" <list>: [[x, y]...] or [] - list of cells that surround killed ship (if it was killed)
        }
    """
    field = FieldJSON.from_session('computer_field')

    try:
        # TODO: check when vars are absent
        x, y = (lambda x, y: (int(x), int(y)))(*request.form.values())
        signal = ShipService.shoot_to(field, x, y)
    except CoordOutOfRange as e:
        return Response(str(e), status=400)
    except (ValueError, TypeError):
        return Response("Required parameters are absent or invalid", status=400)

    hit, response = make_shoot(field, x, y)

    return jsonify(response)


@app.route('/api/computer_shoot', methods=['POST'])
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
    target_field = TargetFieldJSON.from_session('computer_targets')
    user_field = FieldJSON.from_session('user_field')

    x, y = target_field.select_cell()

    hit, response = make_shoot(user_field, x, y)
    target_field.shoot_response(x, y, hit)
    if response.get('border'):
        target_field.mark_killed(response['border'])

    return jsonify(response)
