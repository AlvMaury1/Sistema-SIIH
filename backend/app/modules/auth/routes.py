from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.modules.auth.schemas import LoginRequestSchema, TokenResponseSchema
from app.modules.auth.service import AuthService

auth_bp = Blueprint('auth', __name__)

_login_req = LoginRequestSchema()
_token_res = TokenResponseSchema()


@auth_bp.post('/auth/login')
def login():
    data = _login_req.load(request.get_json())
    resultado = AuthService.login(data)
    return _token_res.dump(resultado), 200


@auth_bp.post('/auth/logout')
@jwt_required()
def logout():
    # get_jwt_identity() devuelve el id_usuario que metimos al hacer login
    user_id = get_jwt_identity()
    AuthService.logout(user_id)
    return {'mensaje': 'Sesión cerrada correctamente.'}, 200
