from dataclasses import dataclass
from marshmallow import Schema, fields, post_load, validate


@dataclass(frozen=True)
class LoginRequest:
    nombre_usuario: str
    password: str


class LoginRequestSchema(Schema):
    nombre_usuario = fields.Str(required=True, validate=validate.Length(min=1))
    password = fields.Str(required=True, validate=validate.Length(min=1))

    @post_load
    def make_dto(self, data, **kwargs):
        return LoginRequest(**data)


class TokenResponseSchema(Schema):
    access_token = fields.Str()
    tipo = fields.Str()
    nombre_usuario = fields.Str()
    rol = fields.Str()
