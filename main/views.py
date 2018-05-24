from flask import render_template, jsonify
from seawar_skeleton import SeaPlayground

from main import app


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/set_all_ships_random')
def set_all_ships_random():
    s = SeaPlayground(10, 10)
    for ship in [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]:
        s.put_ship_random(ship)
    return jsonify([cell.value for cell in s.cells])