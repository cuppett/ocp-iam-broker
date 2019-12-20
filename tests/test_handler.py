import unittest
import broker


class TestHandlerCase(unittest.TestCase):

    def test_response(self):
        print("testing response.")
        result = broker.handler(None, None)
        print(result)
        self.assertEqual(result['statusCode'], 401)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        self.assertIn('Not Authorized', result['body'])


if __name__ == '__main__':
    unittest.main()
