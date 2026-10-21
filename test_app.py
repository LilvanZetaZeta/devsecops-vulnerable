import unittest
from app import app


class TestFlaskApp(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_hello(self):
        response = self.client.get('/hello?name=TEST')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data.decode('utf-8'),
            'Hello, TEST!'
        )


if __name__ == '__main__':
    unittest.main()