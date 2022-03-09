from email.policy import default
from flask_login import UserMixin
from task_manager import db, login_manager
from datetime import datetime

class Tasks(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    task=db.Column(db.Text,nullable=False)
    name=db.Column(db.Integer)
    who=db.Column(db.Integer,default=0)
    date=db.Column(db.DateTime,default=datetime.utcnow)
    check=db.Column(db.Boolean,default=False)
    report=db.Column(db.Text)
    viewed=db.Column(db.Integer,default=0)
    visible=db.Column(db.Boolean,default=True)
    path=db.Column(db.Text)

    def __repr__(self):
        return f'{self.id}'

class Users(db.Model,UserMixin):

    user_id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(120),nullable=False)
    tel=db.Column(db.String(40),default='Телефон не указан')
    password=db.Column(db.Text)
    date=db.Column(db.DateTime,default=datetime.utcnow)
    role=db.Column(db.String(120),default='user')
    email=db.Column(db.Text,default='Email не указан')

    def __repr__(self):
        return f'{self.user_id}'

    def get_id(self):
           return (self.user_id)
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)