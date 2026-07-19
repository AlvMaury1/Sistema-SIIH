from datetime import datetime, timedelta
from flask import current_app
from flask_jwt_extended import create_access_token

from app.extensions import db
from app.modules.auth.models import Usuario
from app.core.security import verify_password
from app.core.errors import ValidationError, ForbiddenError


class AuthService:

    @staticmethod
    def login(data):
        # Equivalente a loadUserByUsername: busca en BD por nombre_usuario
        usuario = Usuario.query.filter_by(nombre_usuario=data.nombre_usuario).first()

        # 404 que mencionaste: el usuario no existe
        # Lo unificamos con credenciales inválidas para no revelar si el usuario existe
        if not usuario:
            raise ValidationError('Credenciales inválidas')

        # Cuenta bloqueada (bloqueo de 15 min tras 3 intentos fallidos)
        if usuario.bloqueado_hasta and usuario.bloqueado_hasta > datetime.utcnow():
            raise ForbiddenError('Cuenta bloqueada. Intente de nuevo en 15 minutos.')

        # 401 que mencionaste: contraseña incorrecta
        if not verify_password(data.password, usuario.hash_password):
            AuthService._registrar_intento_fallido(usuario)
            raise ValidationError('Credenciales inválidas')

        # Login exitoso — resetear contadores y actualizar último acceso
        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None
        usuario.ultimo_acceso = datetime.utcnow()
        db.session.commit()

        # Genera el JWT — identity es el id_usuario (inmutable, no el username)
        # get_jwt_identity() devolverá este valor en cada request protegido
        token = create_access_token(identity=usuario.id_usuario)

        rol = AuthService._obtener_rol(usuario)

        return {
            'access_token': token,
            'tipo': 'Bearer',
            'nombre_usuario': usuario.nombre_usuario,
            'rol': rol,
        }

    @staticmethod
    def _registrar_intento_fallido(usuario):
        max_intentos = current_app.config['MAX_LOGIN_ATTEMPTS']
        minutos = current_app.config['LOCKOUT_MINUTES']

        usuario.intentos_fallidos += 1

        if usuario.intentos_fallidos >= max_intentos:
            usuario.bloqueado_hasta = datetime.utcnow() + timedelta(minutes=minutos)

        db.session.commit()

    @staticmethod
    def logout(user_id):
        usuario = db.session.get(Usuario, user_id)
        if not usuario:
            raise ValidationError('Usuario no encontrado')
        usuario.ultimo_logout = datetime.utcnow()
        db.session.commit()

    @staticmethod
    def _obtener_rol(usuario):
        if usuario.id_personal and usuario.personal:
            return usuario.personal.rol.nombre
        if usuario.id_paciente:
            return 'paciente'
        return None
