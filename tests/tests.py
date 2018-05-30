import unittest


import main


class TestApi(unittest.TestCase):

    def setUp(self):
        self.app = main.app.test_client()

    def test_set_user_ships(self):
        resp = self.app.post('/api/init_user_ship')
        self.assertEqual(resp.status_code, 200)
        data = resp.json

        self.assertEqual(data.keys(), {'max_x', 'max_y', 'cells'})
        self.assertEqual(len(data['cells']), data['max_x'] * data['max_y'])

        for i, cell in enumerate(data['cells']):
            self.assertEqual(cell['y'], i // data['max_x'])
            self.assertEqual(cell['x'], i % data['max_x'])
            # self.assertIn(cell['value'], ['empty', 'ship'])
