import unittest


import seawar_server


class TestApi(unittest.TestCase):

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
