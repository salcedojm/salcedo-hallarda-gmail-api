from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('gmail', '/gmail')
    config.add_route('connected', '/connected')
    config.add_route('get_message', '/get_message')
    config.add_route('refresh_token', '/refresh_token')
    config.add_route('messages', '/messages')
    config.scan()
    return config.make_wsgi_app()
