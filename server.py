from config import Config
from http.server import HTTPServer
from handler import MyHttpRequestHandler


def run(server_class=HTTPServer, handler_class=MyHttpRequestHandler):
    server_address = (Config.HOST, Config.PORT)
    httpd = server_class(server_address, handler_class)
    print(f'Listen port {server_address[1]}...')
    httpd.serve_forever()


if __name__ == '__main__':
    run()
