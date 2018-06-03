import unittest
from unittest.mock import patch

import seawar_server


class TestApiInitFields(unittest.TestCase):

    def setUp(self):
        self.app = seawar_server.app.test_client()

    def test_set_user_ships(self):
        resp = self.app.post('/api/init_user_ship')
        self.assertEqual(resp.status_code, 200)
        data = resp.json
        self.assertEqual(data.keys(), {'max_x', 'max_y', 'ships'})
        self.assertEqual(len(data['ships']), 20) # total number of ship cells. For default 4-3-3-2-2-2-1-1-1-1 == 20

        self.assertEqual(len(data['ships'][0]), 2)
        self.assertEqual(type(data['ships'][0]), list)

    def test_set_comp_ships(self):
        resp = self.app.post('/api/init_enemy_ship')
        self.assertEqual(resp.status_code, 200)
        data = resp.json
        self.assertEqual(data.keys(), {'max_x', 'max_y'})
        self.assertEqual(list(data.values()), [10, 10])


class TestShootShipBase():

    def test_set_user_shoot_miss(self):
        with patch('seawar_server.TargetFieldJSON.select_cell', return_value=(3, 3)), \
             patch('seawar_server.ShipService.shoot_to', return_value=False):
            resp = self.app.post(self.url, data=dict(x=3, y1=3))
        self.assertEqual(resp.status_code, 200)

        data = resp.json
        self.assertEqual(data.keys(), {'signal', 'x', 'y'})
        self.assertEqual(list(data.values()), ['miss', 3, 3])

    def test_set_user_shoot_hit(self):
        with patch('seawar_server.TargetFieldJSON.select_cell', return_value=(3, 3)), \
             patch('seawar_server.ShipService.shoot_to', return_value=True),\
            patch('seawar_server.ShipService.get_ship_if_killed', return_value = {}):
            resp = self.app.post(self.url, data=dict(x=3, y1=3))
        self.assertEqual(resp.status_code, 200)

        data = resp.json
        self.assertEqual(data.keys(), {'signal', 'x', 'y'})
        self.assertEqual(list(data.values()), ['hit', 3, 3])

    def test_set_user_shoot_killed(self):
        ship = [[2, 2], [2, 3], [2, 4]]
        border = [[3, 2], [3, 3], [3, 4]]
        with patch('seawar_server.TargetFieldJSON.select_cell', return_value=(3, 3)), \
             patch('seawar_server.ShipService.shoot_to', return_value=True),\
             patch('seawar_server.ShipService.get_ship_if_killed', return_value = {'ship': ship, 'border': border}), \
             patch('seawar_server.ShipService.is_fleet_killed', return_value = False):
            resp = self.app.post(self.url, data=dict(x=3, y1=3))
        self.assertEqual(resp.status_code, 200)

        data = resp.json
        self.assertEqual(data.keys(), {'signal', 'x', 'y', 'ship', 'border'})
        self.assertEqual(data['signal'], 'killed')
        self.assertEqual(data['x'], 3)
        self.assertEqual(data['y'], 3)
        self.assertEqual(data['ship'], ship)
        self.assertEqual(data['border'], border)

    def test_set_user_shoot_win(self):
        ship = [[2, 2], [2, 3], [2, 4]]
        border = [[3, 2], [3, 3], [3, 4]]
        with patch('seawar_server.TargetFieldJSON.select_cell', return_value=(3, 3)), \
             patch('seawar_server.ShipService.shoot_to', return_value=True),\
             patch('seawar_server.ShipService.get_ship_if_killed', return_value = {'ship': ship, 'border': border}), \
             patch('seawar_server.ShipService.is_fleet_killed', return_value = True):
            resp = self.app.post(self.url, data=dict(x=3, y1=3))
        self.assertEqual(resp.status_code, 200)

        data = resp.json
        self.assertEqual(data.keys(), {'signal', 'x', 'y', 'ship', 'border'})
        self.assertEqual(data['signal'], 'win')
        self.assertEqual(data['x'], 3)
        self.assertEqual(data['y'], 3)


class TestShootShipUser(unittest.TestCase, TestShootShipBase):

    def setUp(self):
        self.app = seawar_server.app.test_client()
        self.url = '/api/user_shoot'

    def test_shoot_outrange(self):
        resp = self.app.post(self.url, data=dict(x=1, y1=333))
        self.assertEqual(resp.status_code, 400)
        self.assertIn(b'out of Field ranges', resp.data)

        resp = self.app.post(self.url, data=dict(x=-11, y1=3))
        self.assertEqual(resp.status_code, 400)
        self.assertIn(b'out of Field ranges', resp.data)

    def test_shoot_coordinate_invalid(self):
        resp = self.app.post(self.url, data=dict(x='test', y1=333))
        self.assertEqual(resp.status_code, 400)
        self.assertIn(b'absent or invalid', resp.data)

        resp = self.app.post(self.url, data=dict(y1=333))
        self.assertEqual(resp.status_code, 400)
        self.assertIn(b'absent or invalid', resp.data)


class TestShootShipComp(unittest.TestCase, TestShootShipBase):

    def setUp(self):
        self.app = seawar_server.app.test_client()
        self.url = '/api/computer_shoot'
