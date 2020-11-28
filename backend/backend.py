#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Backend
Flask API
从数据库读取数据所用API

@Author: MiaoTony
@CreateTime: 20201128
@UpdateTime: 20201129
"""

from secret import *
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine, Table, MetaData, desc
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import math

# os.chdir(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://{}:{}@{}/{}?charset=utf8mb4".format(
    database_username, database_pwd, database_host, database_dbname)
app.config['SQLALCHEMY_TEACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY'] = SECRET_KEY
CORS(app, supports_credentials=True)  # allow CORS

# 建立mysql连接
db_str = "mysql+pymysql://{}:{}@{}/{}".format(
    database_username, database_pwd, database_host, database_dbname)
engine = create_engine(db_str)


class DBinitiall(object):
    # 建立mysql连接并初始化连接池
    def __init__(self, db_str, pool_size):
        self.engine = create_engine(db_str, pool_size=pool_size)
        self.DBsession = sessionmaker(bind=self.engine)

        session_list = list()
        for _ in range(pool_size):
            session = self.DBsession()
            session.connection()
            session_list.append(session)

        for session in session_list:
            session.close()


# 定义模型类继承的父类及数据库连接会话
# 最大连接数为10
DB = DBinitiall(db_str, 10)
dbsession = scoped_session(DB.DBsession)
session = dbsession()
Base = declarative_base()
db = MetaData(bind=DB.engine)


# 定义模型类
class FaceFeature(Base):
    # 面部特征数据库
    __table__ = Table('face_feature', db, autoload=True)


class PicFace(Base):
    # 人 地点 时间 数据库
    __table__ = Table('pic_face', db, autoload=True)


@app.after_request
def after_request(temp_response):
    """
    After a request...
    """
    print("\033[34m#######################################\033[0m")
    return temp_response


# 实时数据路由
@app.route('/api/realtime', methods=['GET'])
def get_realtime_info():
    try:
        print("\033[33m[INFO] Real Time Info:\n", request.url, "\033[0m")
        # print(request.query_string.decode('utf-8'))
        number = request.args.get('num', '')
        page = request.args.get('page', '')
        if not number:
            number = 10
        if int(number) > 30:
            number = 30
        print("num:", number)
        if not page:
            page = 1
        data = session.query(PicFace).order_by(
            desc("pic_time")).limit(number).offset((int(page) - 1) * int(number))
        session.commit()

        info_list = []
        # 将从数据库取得的对象转化为字典类型
        for datas in data:
            dicts = {}
            dicts['person'] = getattr(datas, 'face_id')
            dicts['location'] = getattr(datas, 'pic_gps')
            dicts['time'] = getattr(datas, 'pic_time')
            info_list.append(dicts)
        return jsonify(dict(state=True, msg="ok", data=info_list))

    except Exception as e:
        print('\033[31m[ERROR]', e, '\033[0m')
        session.rollback()
        return jsonify(dict(state=False, msg="ERROR!", data=[]))

    finally:
        session.close()


# 查询某人历史记录路由
@app.route('/api/history/<person_id>', methods=['GET'])
def get_history_info_dis(person_id):
    try:
        print("\033[33m[INFO] History Info:\n", request.url, "\033[0m")
        number = request.args.get('num', '')
        page = request.args.get('page', '')
        if not number:
            number = 10
        if int(number) > 30:
            number = 30
        print("num:", number)
        if not page:
            page = 1
        data = session.query(PicFace).filter(PicFace.face_id == person_id).order_by(
            desc("pic_time")).limit(number).offset((int(page) - 1) * int(number))
        # rows = session.query(PicFace).filter(
        #     PicFace.face_id == person_id).count()
        session.commit()

        path_list = []
        time_list = []
        for datas in data:
            path_list.append(getattr(datas, 'pic_gps'))
            time_list.append(getattr(datas, 'pic_time'))
        info_dict = {"person": person_id, "path": path_list, "time": time_list}
        return jsonify(dict(state=True, msg="ok", data=info_dict))

    except Exception as e:
        print('\033[31m[ERROR]', e, '\033[0m')
        session.rollback()
        return jsonify(dict(state=False, msg="ERROR!", data=[]))

    finally:
        session.close()


# 数据库测试
@app.route('/api/status', methods=['GET', 'POST'])
def api_test():
    """
    Database API test
    """
    # 从request对象读取表单内容
    print('\033[34m[INFO] Database API test!\033[0m')
    raw_data = request.get_data().decode('utf-8')
    print(raw_data)
    try:
        data = session.query(PicFace).count()
        session.commit()
        print(data)
        return jsonify(dict(state=True, msg="Everything looks OK!"))

    except Exception as e:
        print('\033[31m[ERROR]', e, '\033[0m')
        session.rollback()
        return jsonify(dict(state=False, msg="Query ERROR!", data=[]))

    finally:
        session.close()


if __name__ == '__main__':
    app.run(debug=False, port=5000, host='0.0.0.0')  #
