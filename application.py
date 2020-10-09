from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from twilio.rest import Client
import json
import jwt
import random
import datetime
import hashlib, binascii, os
from functools import wraps
import pandas
import sqlalchemy
application = Flask(__name__)

CORS(application)

application.config.from_object("config.DevelopmentConfig")
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
application.config['SQLALCHEMY_POOL_RECYCLE'] = 499
application.config['SQLALCHEMY_POOL_TIMEOUT'] = 20
db = SQLAlchemy(application)

import models

@application.route("/")
def hello():
    return "Hello World!"

@application.route("/login", methods=['POST'])
def login():
    try: 
        dic = json.loads(request.get_data())
        user_name = dic['user_name']
        password = dic['password']
        user=db.session.query(models.Users).filter(models.Users.user_name == user_name).first()

        return jsonify({"id": user.id})

    except Exception as e:
	    return(str(e))
#--------------Users----------------------

@application.route("/add_users", methods = ['POST'])
def add_users():
    dic = json.loads(request.get_data())
    user_name = dic['user_name']
    password = dic['password']
    try:
        users=models.Users(
            password=password,
            user_name=user_name
        )   
        db.session.add(users)
        db.session.commit()
        dic={"usersId":str(users.id)}
        return json.dumps(dic)
    except Exception as e:
	    return(str(e))

#--------------Node----------------------

@application.route("/get_all_nodes")
def get_all_nodes():
    try:
        nodes= db.session.query(models.Node).all()
        return  jsonify([node.serial_number for node in nodes])
    except Exception as e:
	    return(str(e))

@application.route("/add_nodes", methods = ['POST'])
def add_nodes():
    dic = json.loads(request.get_data())
    serial_number = dic['serial_number']

    try:
        nodes=models.Node(
            serial_number=serial_number
        )   
        db.session.add(nodes)
        db.session.commit()
        dic={"serial_number":str(nodes.serial_number)}
        return json.dumps(dic)
    except Exception as e:
	    return(str(e))

#--------------Tests----------------------

@application.route("/get_all_tests")
def get_all_tests():
    try:
        tests= db.session.query(models.Test).all()
        return  jsonify([test.test_name for test in tests])
    except Exception as e:
	    return(str(e))

@application.route("/add_tests", methods = ['POST'])
def add_tests():
    dic = json.loads(request.get_data())
    test_name = dic['test_name']

    try:
        tests=models.Test(
            test_name=test_name
        )   
        db.session.add(tests)
        db.session.commit()
        dic={"test_name":str(tests.test_name)}
        return json.dumps(dic)
    except Exception as e:
	    return(str(e))

#--------------NodeTestResult----------------------

@application.route("/get_all_node_test_results")
def get_all_node_test_results():
    try:
        nodeTestResults= db.session.query(models.NodeTestResult).all()
        return  jsonify([result.serialize() for result in nodeTestResults])
    except Exception as e:
	    return(str(e))

@application.route("/get_results_by_serial_number", methods=['POST'])
def get_results_by_serial_number():
    dic = json.loads(request.get_data())
    serialNumber=dic['serial_number']
    try:
        results = db.session.query(models.NodeTestResult).filter_by(serial_number=serialNumber).all()
        return  jsonify([result.serialize() for result in results])
    except Exception as e:
	    return(str(e))

@application.route("/get_failed_results")
def get_failed_results():
    try:
        results = db.session.query(models.NodeTestResult).filter_by(test_result="Fail").all()
        return  jsonify([result.serialize() for result in results])
    except Exception as e:
	    return(str(e))

@application.route("/get_passed_results")
def get_passed_results():
    try:
        results = db.session.query(models.NodeTestResult).filter_by(test_result="Pass").all()
        return  jsonify([result.serialize() for result in results])
    except Exception as e:
	    return(str(e))

@application.route("/add_excel", methods = ['POST'])
def add_excel():
    dic = json.loads(request.get_data())
    node_array = dic['node_array']
    try:
        count=0
        for i in node_array:
            print(i)
            count+=1
            print(count)
            if "Limits Used" not in i:
                i["Limits Used"]= ""
            if "Comments" not in i:
                i["Comments"]= ""
            if "Test Name" not in i:
                i["Test Name"]= "Test Name Not Recorded"
            if "Test Field" not in i:
                i["Test Field"]= ""
            if "Test Value" not in i:
                i["Test Value"]= ""
            if "Test Result" not in i:
                i["Test Result"]= ""
            if "Spec Name" not in i:
                i["Spec Name"]= ""
            if "Start Time" not in i:
                i["Start Time"]= ""
            if "Stop Time" not in i:
                i["Stop Time"]= ""
            
            if (i["Start Time"] != "Start Time" and i["Stop Time"] != "Stop Time"):
                ntr=models.NodeTestResult(
                    serial_number=i["SN"],
                    test_name=i["Test Name"],
                    test_field=i["Test Field"],
                    test_value=i["Test Value"],
                    test_result=i["Test Result"],
                    spec_name=i["Spec Name"],
                    limits_used=i["Limits Used"],
                    start_time=i["Start Time"],
                    stop_time=i["Stop Time"],
                    comments=i["Comments"]
                )
                if not db.session.query(models.Node).filter_by(serial_number=i["SN"]).first():
                    nodes=models.Node(
                        serial_number=serial_number
                    )
                    db.session.add(nodes)
                if not db.session.query(models.Test).filter_by(test_name=i["Test Name"]).first():
                    tests=models.Test(
                        test_name=test_name
                    )   
                    db.session.add(tests)
                db.session.add(ntr)
        db.session.commit()
        dic={"success":count}
        return json.dumps(dic)
    except Exception as e:
	    return(str(e))

@application.route("/add_node_test_results", methods = ['POST'])
def add_node_test_results():
    dic = json.loads(request.get_data())
    serial_number = dic['serial_number']
    test_name = dic['test_name']
    test_field = dic['test_field']
    test_value = dic['test_value']
    test_result = dic['test_result']
    spec_name = dic['spec_name']
    limits_used = dic['limits_used']
    start_time = dic['start_time']
    stop_time = dic['stop_time']
    comments = dic['comments']

    try:
        ntr=models.NodeTestResult(
            serial_number=serial_number,
            test_name=test_name,
            test_field=test_field,
            test_value=test_value,
            test_result=test_result,
            spec_name=spec_name,
            limits_used=limits_used,
            start_time=start_time,
            stop_time=stop_time,
            comments=comments
        )   
        db.session.add(ntr)
        db.session.commit()
        dic={"id":str(ntr.id)}
        return json.dumps(dic)
    except Exception as e:
	    return(str(e))

if __name__ == '__main__':
    application.run(host='0.0.0.0', port='4000')