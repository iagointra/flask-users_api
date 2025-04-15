from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db_users.db'
db = SQLAlchemy(app)
api = Api(app)

class UserModel(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_login = db.Column(db.String(256), unique=True, nullable=False)
    user_name = db.Column(db.String(256), unique=True, nullable=False)
    user_status = db.Column(db.Boolean, default=True, nullable=False)
    user_createdAt = db.Column(db.DateTime, default=datetime.now, nullable=False)
    user_updatedAt = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    def __repr__(self):
        return f"User(login = {self.user_login}, name = {self.user_name})"

user_args = reqparse.RequestParser()
user_args.add_argument('user_login', type=str, required=True, help="User login cannot be blank")
user_args.add_argument('user_name', type=str, required=True, help="User name cannot be blank")
user_args.add_argument('user_status', type=bool, required=True, help="User name cannot be blank")

userFields = {
    "user_id":fields.Integer,
    "user_login":fields.String,
    "user_name":fields.String,
    "user_status":fields.Boolean,
    "user_createdAt": fields.DateTime(dt_format='iso8601'),
    "user_updatedAt": fields.DateTime(dt_format='iso8601')
}

class Users(Resource):
    @marshal_with(userFields)
    def get(self):
        users = UserModel.query.all()
        return users

    @marshal_with(userFields)
    def post(self):
        args = user_args.parse_args()
        user = UserModel(user_login=args["user_login"], user_name=args["user_name"])
        db.session.add(user)
        db.session.commit()
        users = UserModel.query.all()
        return users, 201
    
class User(Resource):
    @marshal_with(userFields)
    def get(self, user_id):
        user = UserModel.query.filter_by(user_id=user_id).first()
        if not user:
            abort(404, "User not found")
        return user
    
    @marshal_with(userFields)
    def patch(self, user_id):
        args = user_args.parse_args()
        user = UserModel.query.filter_by(user_id=user_id).first()
        if not user:
            abort(404, "User not found")
        user.user_login = args["user_login"]
        user.user_name = args["user_name"]
        user.user_status = args["user_status"]
        db.session.commit()
        return user

class ActiveUsers(Resource):
    @marshal_with(userFields)
    def get(self):
        active_users = UserModel.query.filter_by(user_status=True).all()
        return active_users

class InactiveUsers(Resource):
    @marshal_with(userFields)
    def get(self):
        inactive_users = UserModel.query.filter_by(user_status=False).all()
        return inactive_users

api.add_resource(Users, '/api/users')
api.add_resource(User, '/api/users/<int:user_id>')
api.add_resource(InactiveUsers, '/api/users/inactive')
api.add_resource(ActiveUsers, '/api/users/active')

@app.route('/')
def home():
    return '<h1>Flask REST API</h1>'

if __name__ == '__main__':
    app.run(debug=True)