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
		kwargs = {k:v for k,v in kwargs.items() if k is not False}
		resp = self.session.get(self.api_url, params={'action':action,'format':'json', **kwargs})
		if resp.status_code != 200:
			print(resp, resp.text)
		json = resp.json()
		if 'error' in json:
			raise ValueError(resp.json())
		if 'warnings' in resp:
			raise ValueError(resp)
		return json

	def post(self, action, **kwargs):
		kwargs = {k:v for k,v in kwargs.items() if k is not False}
		resp = self.session.post(self.api_url, params={'action':action,'format':'json'}, data=kwargs)
		if resp.status_code != 200:
			print(resp, resp.text)
		json = resp.json()
		if 'error' in json:
			raise ValueError(resp.json())
		return json

	def query(self, resp_key, limit=0, **kwargs):
		resp = None
		data = {}
		count = 0

		while resp is None or ((limit == 0 or count < limit) and 'continue' in resp):
			resp = self.get('query', **kwargs)
			if 'continue' in resp:
				kwargs.update(resp['continue'])
			if type(resp['query'][resp_key]) == list:
				assert 'batchcomplete' in resp
				for x in resp['query'][resp_key]:
					yield x
				continue

			for k,v in resp['query'][resp_key].items():
				if k not in data:
					data[k] = v
				else:
					for sk, sv in v.items():
						if sk in data[k] and type(sv) == list:
							data[k][sk].extend(sv)
						else:
							data[k][sk] = sv
			if 'batchcomplete' in resp:
				for x in data.values():
					yield x
					count += 1
				data.clear()

	def token(self, type='csrf'):
		return self.get('query', meta='tokens', type=type)['query']['tokens'][type+'token']

	def login(self, username, password):
		resp = self.post('login', lgname=username, lgpassword=password, lgtoken=self.token('login'))
		assert resp['login']['result'] == 'Success'
		self.userid = resp['login']['lguserid']
		self.username = resp['login']['lgusername']

	def myrights(self):
		return self.get('query', list='users', ususers=self.username, usprop='rights')['query']['users'][0]['rights']

def join(things):
	return '|'.join([str(t) for t in things])
