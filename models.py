from application import db
from sqlalchemy.orm import aliased
from sqlalchemy.orm import backref

class Users(db.Model):
    _tablename_ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(20))
    user_name = db.Column(db.String(20))

    def __init__(self, password, user_name):
        self.password = password
        self.user_name = user_name

    def __repr__(self):
        return '<id {}>'.format(self.id)
    
    def serialize(self):
        return {
            'id': self.id, 
            'password': self.password,
            'user_name': self.user_name
        }

class Node(db.Model):
    _tablename_ = 'node'

    serial_number = db.Column(db.String(20), primary_key=True)

    def __init__(self, serial_number):
        self.serial_number = serial_number
    
    def serialize(self):
        return {
            'serial_number': self.serial_number
        }

class Test(db.Model):
    _tablename_ = 'test'

    test_name = db.Column(db.String(50), primary_key=True)

    def __init__(self, test_name):
        self.test_name = test_name

    def serialize(self):
        return {
            'test_name': self.test_name
        }

class NodeTestResult(db.Model):
    _tablename_ = 'node_test_result'

    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(20), db.ForeignKey('node.serial_number'), nullable=False)
    test_name = db.Column(db.String(50), db.ForeignKey('test.test_name'), nullable=False)
    test_field = db.Column(db.String(50))
    test_value = db.Column(db.Float, nullable=False)
    test_result = db.Column(db.String(10), nullable=False)
    spec_name = db.Column(db.String(50))
    limits_used = db.Column(db.String(20))
    start_time = db.Column(db.DateTime)
    stop_time = db.Column(db.DateTime)
    comments = db.Column(db.String(50))

    def __init__(self, serial_number, test_name, test_field, test_value, test_result, spec_name, limits_used, start_time, stop_time, comments):
        self.serial_number = serial_number
        self.test_name = test_name
        self.test_field = test_field
        self.test_value = test_value
        self.test_result = test_result
        self.spec_name = spec_name
        self.limits_used = limits_used
        self.start_time = start_time
        self.stop_time = stop_time
        self.comments = comments

    def __repr__(self):
        return '<id {}>'.format(self.id)
    
    def serialize(self):
        return {
            'id': self.id, 
            'serial_number': self.serial_number,
            'test_name': self.test_name,
            'test_field': self.test_field,
            'test_value': self.test_value,
            'test_result': self.test_result,
            'spec_name': self.spec_name,
            'limits_used': self.limits_used,
            'start_time': self.start_time,
            'stop_time': self.stop_time,
            'comments': self.comments
        }
