import requests

NS_MAIN = 0
NS_USER = 2
NS_PROJECT = 4
NS_FILE = 6
NS_MEDIAWIKI = 8
NS_TEMPLATE = 10
NS_HELP = 12
NS_CATEGORY = 14

class MWException(Exception):
	pass

def _dmerge(source, destination):
	for key, value in source.items():
		if isinstance(value, dict):
			node = destination.setdefault(key, {})
			_dmerge(value, node)
		elif isinstance(value, list):
			node = destination.setdefault(key, [])
			node.extend(value)
		else:
			destination[key] = value
	return destination

def chunks(l, n):
	"""Yield successive n-sized chunks from l."""
	for i in range(0, len(l), n):
		yield l[i:i + n]

class Site():
	def __init__(self, api_url):
		self.api_url = api_url
		self.session = requests.session()

	def request(self, method, action, params, data):
		params = {k:v for k,v in params.items() if k is not False}
		data   = {k:v for k,v in data.items()   if k is not False}
		resp = self.session.request(method, self.api_url, params={'action':action,'format':'json', **params}, data=data)
		if resp.status_code != 200:
			print(resp, resp.text)
		json = resp.json()
		if 'error' in json:
			raise MWException(json['error'])
		if 'warnings' in resp:
			raise MWException(json['warnings'])
		return json

	def post(self, action, **kwargs):
		return self.request('post', action, {}, kwargs)

	def get(self, action, **kwargs):
		return self.request('get', action, kwargs, {})

	def merge_dicts(a, b):
		for k, v in b.items():
			if k in a and type(v) == list:
				a[k].extend(v)
			else:
				a[k] = v

	def results(self, **kwargs):
		for batch in self.batches(**kwargs):
			results = batch[kwargs.get('list', 'pages')]
			if type(results) == list:
				for r in results: yield r
			elif type(results) == dict:
				for r in results.values(): yield r

	def complete(self, **kwargs):
		data = {}
		for batch in self.batches(**kwargs):
			_dmerge(batch, data)
		return data

	def batches(self, **kwargs):
		data = {}
		resp = None

		while resp is None or 'continue' in resp:
			resp = self.post('query', **kwargs)
			_dmerge(resp['query'], data)

			if 'batchcomplete' in resp:
				yield data
				data = {}

			if 'continue' in resp:
				kwargs.update(resp['continue'])

	def token(self, type='csrf'):
		return self.post('query', meta='tokens', type=type)['query']['tokens'][type+'token']

	def login(self, username, password):
		resp = self.post('login', lgname=username, lgpassword=password, lgtoken=self.token('login'))
		assert resp['login']['result'] == 'Success'
		self.userid = resp['login']['lguserid']
		self.username = resp['login']['lgusername']

	def require_rights(self, rights):
		my_rights = self.post('query', list='users', ususers=self.username, usprop='rights')['query']['users'][0]['rights']
		for r in rights:
			if r not in my_rights:
				raise MWException('account lacks permission: {}'.format(r))

def join(things):
	return '|'.join([str(t) for t in things])
