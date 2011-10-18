import os
import urlparse

# WSGI library
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.utils import redirect

# Templating language modelled after Django
from jinja2 import Environment, FileSystemLoader

# A WSGI application
class Todo(object):
	def __init__(self):
		t_path = os.path.join(os.path.dirname(__file__), 'templates')
		self.jinja_env = Environment(loader=FileSystemLoader(t_path), autoescape=True)
		self.url_map = self.create_url_map()

	def create_url_map(self):
		return Map([
			Rule('/', endpoint='root'),
			Rule('/<string>', endpoint='hello'),
		])

	# All additional arguments in a dictionary called context
	def render_template(self, template_name, **context):
		t = self.jinja_env.get_template(template_name)
		return Response(t.render(context), mimetype='text/html')

	# Dispatch requests to the on_<blah> method
	def dispatch_request(self, request):
		adapter = self.url_map.bind_to_environ(request.environ)
		try:
			endpoint, values = adapter.match()
			return getattr(self, 'on_' + endpoint)(request, **values)
		except HTTPException, e:
			return e

	def on_root(self, request):
		return self.render_template('index.html')

	# Called when we get hit
	def __call__(self, environ, start_response):
		rqst = Request(environ)
		rsp = self.dispatch_request(rqst)
		return rsp(environ, start_response)

# Launch server, export static dir to the world
if __name__ == '__main__':
	from werkzeug.serving import run_simple
	app = Todo()
	app.wsgi_app = SharedDataMiddleware(app.__call__, {
		'/static': os.path.join(os.path.dirname(__file__), 'static')
	})
	run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)
