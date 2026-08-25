from routes.dashboard import init_routes as init_dashboard_routes
from routes.pesquisa import init_routes as init_pesquisa_routes
from routes.admin_formulario import init_routes as init_admin_formulario_routes
from routes.admin_ciclos import init_routes as init_admin_ciclos_routes
from routes.admin_formularios import init_routes as init_admin_formularios_routes

def init_all_routes(app):
    init_dashboard_routes(app)
    init_pesquisa_routes(app)
    init_admin_formulario_routes(app)
    init_admin_ciclos_routes(app)
    init_admin_formularios_routes(app)
