from flask import Blueprint

documentos_bp = Blueprint('documentos', __name__)

# TODO: POST /api/documentos          — subida autenticada
# TODO: GET  /api/documentos/<id>     — descarga autenticada con send_file
