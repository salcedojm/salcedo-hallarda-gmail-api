from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
my_session_factory = SignedCookieSessionFactory('itsaseekreet')

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)  
    config.set_session_factory(my_session_factory)
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('gmail', '/gmail')
    config.add_route('connected', '/connected')
    config.add_route('get_message', '/get_message')
    config.add_route('send_message_view', '/send_message_view')
    config.add_route('send_message', '/send_message')
    config.add_route('actions', '/actions')
    config.add_route('get_message_list', '/get_message_list')
    config.add_route('message_list', '/message_list')
    config.scan()
    return config.make_wsgi_app()
