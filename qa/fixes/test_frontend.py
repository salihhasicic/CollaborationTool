import unittest
from unittest.mock import patch, Mock
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from main import app

class FrontendEdgeTests(unittest.TestCase):
    def test_expired_cookie_does_not_block_public_registration(self):
        client = app.test_client()
        client.set_cookie('jwt_token', 'expired-token')
        response = Mock(ok=True, status_code=200)
        response.json.return_value = [{'id': 1, 'name': 'Dev Team'}]
        with patch('main.requests.request', return_value=response) as call:
            result = client.get('/register')
        self.assertEqual(result.status_code, 200)
        self.assertNotIn('Authorization', call.call_args.kwargs['headers'])

    def test_zero_coordinates_remain_visible_and_editable(self):
        from flask import render_template
        with app.test_request_context('/profile/1'):
            html = render_template('profile.html', user={'id':1,'username':'zero','latitude':0,'longitude':0,'skills':'','location':'','team_id':None,'photo_url':'/static/avatar.svg'})
        self.assertIn('id="display-lat">0</span>', html)
        self.assertIn('id="input-lat" value="0"', html)
        self.assertIn('id="display-lng">0</span>', html)

if __name__ == '__main__':
    unittest.main()
