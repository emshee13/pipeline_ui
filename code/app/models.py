'''
BIOT670 Initial database module for pipeline UI
taken from https://github.com/hack4impact/flask-base/blob/master/app/models/user.py

'''

from flask import Flask, flash, redirect, url_for, request, render_template, Response, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, AnonymousUserMixin
from flask_login import LoginManager, current_user, login_required, login_user
#from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
#from itsdangerous import BadSignature, SignatureExpired
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import Table, ForeignKey, Column, Integer
from sqlalchemy.orm import relationship



db = SQLAlchemy()


user_role = db.Table('user_role', db.Model.metadata,
    db.Column('user_id', db.Integer, ForeignKey('users.id')),
    db.Column('role_id', db.Integer, ForeignKey('roles.id')),
)

class User(UserMixin, db.Model):
    """
    User class. Your Typical user class.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    confirmed = db.Column(db.Boolean, default=False)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    roles = db.relationship(
        "Role",
        secondary=user_role,
        )

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def can(self, permission):
        if any(r for r in current_user.roles if r.name==permission):
           return True

    def assign_role(self, role):
        if self not in User.query.filter(User.roles.any(name=role)).all():
            assignment = Role.query.filter(Role.name == role).first()
            self.roles.append(assignment)
            db.session.add(self)
            db.session.commit()
            flash('Role granted successfully.','success')
        else:
            flash('Role already granted.', 'error')

    @property
    def password(self):
        raise AttributeError('`password` is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User \'%s\'>' % self.full_name()

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    index = db.Column(db.String(64))
    default = db.Column(db.Boolean, default=False, index=True)

    @staticmethod
    def insert_roles():
        roles = {
            'Placeholder1': ('placeholder1', False),
            'Placeholder2': ('placeholder2', False),
            'Administrator': (
                'admin',
                False
            )
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.index = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role \'%s\'>' % self.name

    def create_role(role):
        db_role = Role.query.filter_by(name=role).first()
        if db_role:
            flash('Role already exists','error')
        else:
            new_role = Role(name=role)
            new_role.index = role
            new_role.default = False
            db.session.add(new_role)
            db.session.commit()


login_manager = LoginManager()
login_manager.login_view = 'login'

class AnonymousUser(AnonymousUserMixin):
    def can(self, _):
        return False


login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user

@login_manager.unauthorized_handler
def unauthorized():
    return(
    Response("You must be logged in to view that page."),
    401,
    )

# The home page should have 5 tabs, each capable of performing some type of request handling
# the data for each tab will be stored in the RequestDetails tables

class RequestDetails(db.Model):
    Id = db.Column(db.Integer, primary_key=True)
    requestData = db.Column(db.CHAR(None), unique=False, nullable=True)
    status = db.Column(db.String(20), unique=False, nullable=True)
    createDate = db.Column(db.DateTime, unique=False, nullable=False)
    userId = db.Column(db.Integer, unique=False, nullable=False)
    errorMessage = db.Column(db.String(100), unique=False, nullable=False)

    def __init__(self, requestData, status, createDate, userId, errorMessage):
        self.requestData = requestData
        self.status = status
        self.createDate = createDate
        self.userId = userId
        self.errorMessage = errorMessage
