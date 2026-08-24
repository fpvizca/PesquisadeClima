from routes.pesquisa import init_routes as init_pesquisa_routes
from routes.admin_formulario import init_routes as init_admin_formulario_routes

def init_all_routes(app):
    init_pesquisa_routes(app)
    init_admin_formulario_routes(app)
