import requests

NS_MAIN = 0
NS_USER = 2
NS_PROJECT = 4
NS_FILE = 6
NS_MEDIAWIKI = 8
NS_TEMPLATE = 10
NS_HELP = 12
NS_CATEGORY = 14

class Site():
	def __init__(self, api_url):
		self.api_url = api_url
		self.session = requests.session()

	def get(self, action, **kwargs):
		resp = self.session.get(self.api_url, params={'action':action,'format':'json', **kwargs})
		if resp.status_code != 200:
			print(resp, resp.text)
		json = resp.json()
		if 'error' in json:
			raise ValueError(resp.json())
		return json

	def post(self, action, **kwargs):
		resp = self.session.post(self.api_url, params={'action':action,'format':'json'}, data=kwargs)
		if resp.status_code != 200:
			print(resp, resp.text)
		json = resp.json()
		if 'error' in json:
			raise ValueError(resp.json())
		return json

	def query(self, resp_key, cont={}, **kwargs):
		resp = self.get('query', **kwargs)

		# TODO: detect error status codes
		if 'warnings' in resp:
			raise ValueError(resp)

		results = resp['query'][resp_key]
		if type(results) == dict:
			results = results.values()
		for r in results:
			yield r

		if 'continue' in resp:
			kwargs.update(resp['continue'])
			for r in self.query(resp_key, **kwargs):
				yield r

	def token(self, type='csrf'):
		return self.get('query', meta='tokens', type=type)['query']['tokens'][type+'token']

	def login(self, username, password):
		resp = self.post('login', lgname=username, lgpassword=password, lgtoken=self.token('login'))
		assert resp['login']['result'] == 'Success'
		self.userid = resp['login']['lguserid']
		self.username = resp['login']['lgusername']

	def myrights(self):
		return self.get('query', list='users', ususers=self.username, usprop='rights')['query']['users'][0]['rights']
