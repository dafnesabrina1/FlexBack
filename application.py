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
import re
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

#--------------NodeTestResult----------------------

@application.route("/get_all_tests")
def get_all_node_test_results():
    try:
        nodeTestResults= db.session.query(models.Tests).all()
        return  jsonify([result.serialize() for result in nodeTestResults])
    except Exception as e:
	    return(str(e))

@application.route("/get_results_by_serial_number", methods=['POST'])
def get_results_by_serial_number():
    dic = json.loads(request.get_data())
    serialNumber=dic['sn']
    try:
        results = db.session.query(models.Tests).filter_by(sn=serialNumber).all()
        return  jsonify([result.serialize() for result in results])
    except Exception as e:
	    return(str(e))

@application.route("/get_failed_results")
def get_failed_results():
    try:
        results = db.session.query(models.Tests).filter_by(test_result="Fail").all()
        return  jsonify([result.serialize() for result in results])
    except Exception as e:
	    return(str(e))

@application.route("/get_passed_results")
def get_passed_results():
    try:
        results = db.session.query(models.Tests).filter_by(test_result="Pass").all()
        return  jsonify([result.serialize() for result in results])
    except Exception as e:
	    return(str(e))

@application.route("/get_tests_with_limits")
def get_tests_with_limits():
    try:
        results = db.session.query(models.Tests).filter(models.Tests.limits_used.isnot(None)).all()
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
            
            ntr=models.Tests(
                sn=i["SN"],
                s_no=i["S_NO"],
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

            db.session.add(ntr)
        db.session.commit()
        dic={"success":count}
        return json.dumps(dic)
    except Exception as e:
	    return(str(e))

@application.route("/add_test", methods = ['POST'])
def add_node_test_results():
    dic = json.loads(request.get_data())
    sn = dic['sn']
    s_no = dic['s_no']
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
            sn=sn,
            s_no=s_no,
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
        dic={"SN":str(ntr.sn), "S_NO": str(ntr.s_no)}
        return json.dumps(dic)
    except Exception as e:
	    return(str(e))

@application.route("/get_unique_sn")
def get_unique_sn():
    try: 
        rs = db.session.query(models.Tests.sn).group_by(models.Tests.sn).all()
        return jsonify([result.sn for result in rs])
    except Exception as e:
	    return(str(e))  

@application.route("/last_tests_of_sn", methods=["POST"])
def last_tests_of_sn():
    dic = json.loads(request.get_data())
    sn = dic['sn']
    try: 
        rs = db.session.query(models.Tests.limits_used, models.Tests.test_name, models.Tests.stop_time, models.Tests.test_value).filter(models.Tests.limits_used.isnot(None)).filter(models.Tests.limits_used != "").filter_by(sn=sn).order_by(models.Tests.test_name).all()
        res= []
        test=""
        time=[]
        test_to_add={}
        count = 0
        for i in rs:
            count+=1
            if test == "" and len(i.limits_used.split()) == 5:
                test= i.test_name
                time= re.split(r"[ :/-]+", i.stop_time)
                test_to_add= i
            elif i.test_name != test:
                if test_to_add != {}:
                    res.append(test_to_add)
                    if len(i.limits_used.split()) == 5:
                        test= i.test_name
                        time= re.split(r"[ :/-]+", i.stop_time)
                        test_to_add= i
                    else:
                        test = ""
                        time=[]
                        test_to_add={}
            elif i.test_name == test and len(i.limits_used.split()) == 5 and older_than(time, re.split(r"[ :/-]+", i.stop_time)):
                time= re.split(r"[ :/-]+", i.stop_time)
                test = i.test_name
                test_to_add= i
        if test_to_add != {}:    
            res.append(test_to_add)
        return jsonify([{"limits_used": result.limits_used, "test_name": result.test_name, "stop_time": result.stop_time, "test_value": result.test_value} for result in res[:2]])
    except Exception as e:
	    return(str(e)) 

def older_than(old, new):
    if old == new:
        return True
    if old[2] < new[2]:
        return True
    else:
        if old[0] < new[0]:
            return True
        else:
            if old[1] < new[1]:
                return True
            else:
                if old[3] < new[3]:
                    return True
                    if old[4] < new[4]:
                        return True
    return False



if __name__ == '__main__':
    application.run(host='0.0.0.0', port='4000')