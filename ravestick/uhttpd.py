import gc
import sys

import uasyncio as asyncio

VERSION = "master"


class NotFoundException(Exception):
	pass


class BadRequestException(Exception):
	pass


class ForbiddenException(Exception):
	pass


def get_relative_path(http_request):
	path = http_request['path']
	prefix = http_request['prefix']
	return path[len(prefix):]


class Server:
	def __init__(self, handlers, config={}):
		self._handlers = handlers
		self._config = self.update(self.default_config(), config)
		self._tcp_server = TCPServer(
			bind_addr=self._config['bind_addr'],
			port=self._config['port'],
			#timeout=self._config['timeout'],
			handler=self,
			backlog=self._config['backlog']
		)

	def run(self):
		self._tcp_server.run()

	def handle_request(self, reader, writer, tcp_request):
		http_request = {
			'tcp': tcp_request
		}
		try:
			#
			# parse out the heading line, to get the verb, path, and protocol
			#
			line = yield from reader.readline()
			print(line)
			heading = self.parse_heading(line.decode('UTF-8'))
			http_request.update(heading)
			#
			# find the handler for the specified path.  If we don't have
			# one registered, we raise a NotFoundException, but only after
			# reading the payload.
			#
			path = http_request['path']
			handler = None
			for prefix, h in self._handlers:
				if path.startswith(prefix):
					http_request['prefix'] = prefix
					handler = h
					break
			#
			# Parse out the headers
			#
			headers = {}
			num_headers = 0
			while True:
				line = yield from reader.readline()
				if not line or line == b'\r\n':
					break
				k, v = Server.parse_header(line.decode('UTF-8'))
				headers[k.lower()] = v
				num_headers += 1
				if num_headers > self._config['max_headers']:
					raise BadRequestException("Number of headers exceeds maximum allowable")
			http_request['headers'] = headers
			#
			# If the headers have a content length, then read the body
			#
			#content_length = 0
			if 'content-length' in headers:
				content_length = int(headers['content-length'])
				if content_length > self._config['max_content_length']:
					raise BadRequestException("Content size exceeds maximum allowable")
				elif content_length > 0:
					body = yield from reader.read(content_length)
					http_request['body'] = body
			#
			# If there is no handler, then raise a NotFound exception
			#
			if not handler:
				raise NotFoundException("No Handler for path {}".format(path))
			# get the response from the active handler and serialize it
			# to the socket
			#
			response = handler.handle_request(http_request)
			return (yield from Server.response(writer, response))
		except BaseException as e:
			return (yield from Server.internal_server_error(writer, e))

	#
	# Internal operations
	#

	@staticmethod
	def update(a, b):
		a.update(b)
		return a

	@staticmethod
	def default_config():
		return {
			'bind_addr': '0.0.0.0',
			'port': 80,
			#'timeout': 30,
			'max_headers': 25,
			'max_content_length': 1024,
			'backlog': 5
		}

	#def readline(self, client_socket):
	#	return client_socket.readline()

	@staticmethod
	def parse_heading(line):
		ra = line.split()
		try:
			return {
				'verb': ra[0].lower(),
				'path': ra[1],
				'protocol': ra[2]
			}
		except:
			raise BadRequestException("Error splitting parsing heading into verb path protocol")

	@staticmethod
	def parse_header(line):
		ra = line.split(":")
		return (ra[0].strip(), ra[1].strip())

	@staticmethod
	def server_name():
		return "uhttpd/{} (running in your devices)".format(VERSION)

	@staticmethod
	def format_heading(code):
		return "HTTP/1.1 {} {}".format(code, Server.lookup_code(code))

	@staticmethod
	def lookup_code(code):
		if code == 200:
			return "OK"
		elif code == 400:
			return "Bad Request"
		elif code == 403:
			return "Forbidden"
		elif code == 404:
			return "Not Found"
		elif code == 500:
			return "Internal Server Error"
		else:
			return "Unknown"

	@staticmethod
	def format_headers(headers):
		ret = ""
		for k, v in headers.items():
			ret += "{}: {}\r\n".format(k, v)
		return ret

	@staticmethod
	def response(client_socket, response):
		yield from Server.serialize(client_socket, response)
		return (True, None)

	@staticmethod
	def serialize(stream, response):
		#
		# write the heading and headers
		#
		yield from stream.awrite("{}\r\n{}\r\n".format(
			Server.format_heading(response['code']),
			Server.format_headers(Server.update(
				response['headers'], {'Server': Server.server_name()}
			))
		).encode('UTF-8'))
		#
		# Write the body, if it's present
		#
		if 'body' in response:
			body = response['body']
			if body:
				yield from body(stream)
	@staticmethod
	def internal_server_error(writer, e):
		sys.print_exception(e)
		error_message = "Internal Server Error: {}".format(e)
		return (yield from Server.error(writer, 500, error_message, e))

	@staticmethod
	def error(writer, code, error_message, e, headers={}):
		ef = lambda stream: (yield from Server.stream_error(writer, error_message, e))
		response = Server.generate_error_response(code, ef, headers)
		return (yield from Server.response(writer, response))

	@staticmethod
	def stream_error(writer, error_message, e):
		yield from writer.awrite(error_message)
		if e:
			yield from writer.awrite('<pre>')
			yield from writer.awrite(Server.stacktrace(e))
			yield from writer.awrite('</pre>')

	@staticmethod
	def stacktrace(e):
		import uio
		buf = uio.BytesIO()
		sys.print_exception(e, buf)
		return buf.getvalue()

	@staticmethod
	def generate_error_response(code, ef, headers={}):
		data1 = '<html><body><header>uhttpd/{}<hr></header>'.format(
			VERSION).encode('UTF-8')
		# message data in ef will go here
		data2 = '</body></html>'.encode('UTF-8')
		body = lambda writer: (yield from Server.write_html(writer, data1, ef, data2))
		return {
			'code': code,
			'headers': Server.update({
				'content-type': "text/html",
			}, headers),
			'body': body
		}

	@staticmethod
	def write_html(writer, data1, ef, data2):
		yield from writer.awrite(data1)
		yield from ef(writer)
		yield from writer.awrite(data2)


class TCPServer:
	def __init__(self, port, handler, bind_addr='0.0.0.0',
				 #timeout=30,
				 backlog=10):
		self._port = port
		self._handler = handler
		self._bind_addr = bind_addr
		#self._timeout = timeout
		self._backlog = backlog

	def handle_receive(self, reader, writer, tcp_request):
		try:
			done, response = yield from self._handler.handle_request(reader, writer, tcp_request)
			if response and len(response) > 0:
				yield from writer.awrite(response)
			if done:
				return False
			else:
				return True
		except Exception as e:
			sys.print_exception(e)
			return False

	def serve(self, reader, writer):
		tcp_request = {
			'remote_addr': writer.extra["peername"]
		}
		gc.collect()
		try:
			while (yield from self.handle_receive(reader, writer, tcp_request)):
				gc.collect()
		finally:
			yield from writer.aclose()
			gc.collect()

	def run(self, debug=False):

		loop = asyncio.get_event_loop()
		this = self

		@asyncio.coroutine
		def serve(reader, writer):
			yield from this.serve(reader, writer)

		loop.call_soon(asyncio.start_server(
			client_coro=serve,
			host=self._bind_addr,
			port=self._port,
			backlog=self._backlog
		))
		loop.run_forever()
		loop.close()
