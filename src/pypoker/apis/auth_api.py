from flask import Flask, Blueprint, current_app, jsonify, request
from flask_restplus import (
    Resource, fields, Namespace, reqparse, inputs)
from .api_decorators import token_required
from ..models.user import User


api = Namespace(
    'auth', description='Authentication related operations')


register_parser = api.parser()
register_parser.add_argument(
    'Username', 
    type=inputs.regex('^[a-zA-Z][a-zA-Z0-9\.]{1,16}$'),
    required=True, location='form')
register_parser.add_argument(
    'Password', 
    type=inputs.regex('^[A-Za-z0-9@\!\?\$\-\_\.\*\(\)]{4,24}$'),
    required=True, location='form')
register_parser.add_argument('Email', 
    type=inputs.regex('[^@]+@[^@]+\.[^@]+'),
    required=True, location='form')
register_parser.add_argument(
    'ScreenName', 
    type=inputs.regex('^[A-Za-z0-9@\!\?\$\-\_\.\*\(\)]{1,24}$'),
    location='form')

@api.route("/register")
class Register(Resource):
    @api.doc(parser=register_parser)
    def post(self):
        data = register_parser.parse_args()
        user = User(data['Username'], 
                    data['Password'],
                    data['Email'],
                    screen_name=data['ScreenName'])
        if not user.create():
            return {
                'errors': 
                    {'error': 'Internal Server Error'},
                'message': 'User could not be created'
            }, 500
        return {'data': user.as_dict()}, 200


login_parser = api.parser()
login_parser.add_argument(
    'Identifier', 
    type=inputs.regex('^[a-zA-Z][a-zA-Z0-9@\.]{1,16}$'), 
    required=True, help='Username or Email', location='form')
login_parser.add_argument(
    'Password', 
    type=inputs.regex('^[A-Za-z0-9@\!\?\$\-\_\.\*\(\)]{4,24}$'),
    required=True, location='form')

@api.route("/login")
class Login(Resource):
    @api.doc(parser=login_parser)
    def post(self):
        data = login_parser.parse_args()
        password = data['Password']  
        user = User.fetch(email=data['Identifier']) \
            if '@' in data['Identifier'] \
            else User.fetch(username=data['Identifier'])
        if user is None:
            return {
                'errors': {'Identifier': 'User does not exist'},
                'message': 'Invalid username or email'
                }, 401
        if not user.verify_password(password):
            return {
                'errors': {'Password': 'Invalid password'},
                'message': 'Invalid password'
                }, 401
        return {'token': user.generate_auth_token()}, 200


@api.route("/check-login")
class CheckLogin(Resource):
    @api.doc(security='apikey')
    @token_required
    def get(self):
        return {'message': 'User is logged in'}, 200

