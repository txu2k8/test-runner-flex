#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:sqlalchemy_opt
@time:2022/08/21
@email:tao.xu2008@outlook.com
@description:
"""
import os
import unittest
from loguru import logger

from testrunner.config import root_dir, DB_INFO
from sqlalchemy import Column, String, create_engine, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 创建对象的基类:
Base = declarative_base()


class SqlalchemyOperation(object):
    """sqlalchemy ORM操作"""
    def __init__(self, db_info):
        self.db_info = db_info
        self.engine = None
        self.create_engine()

        # 创建DBSession类型:
        self.db_session = sessionmaker(bind=self.engine)
        # 创建session对象:
        self.session = self.db_session()

    def create_engine(self):
        if DB_INFO.get('ENGINE') == 'django.db.backends.sqlite3':
            # db_path = db_info.get('NAME')
            db_path = os.path.abspath(os.path.join(root_dir, 'test_db.sqlite3'))
            logger.info(db_path)
            self.engine = create_engine(r'sqlite:///{}'.format(db_path))
        elif DB_INFO.get('ENGINE') == 'django.db.backends.mysql':
            user = DB_INFO.get('USER')
            password = DB_INFO.get('PASSWORD')
            host = DB_INFO.get('HOST')
            port = DB_INFO.get('PORT')
            name = DB_INFO.get('NAME')
            self.engine = create_engine('mysql+pymysql://root:******@localhost:3306/scheduler')
        else:
            logger.critical("错误的数据库类型，将跳过结果写入！")

    # 创建所有定义的表到数据库中
    def init_db(self):
        Base.metadata.create_all(self.engine)

    # 从数据库中删除所有定义的表
    def drop_db(self):
        Base.metadata.drop_all(self.engine)


# 定义User对象:
class User(Base):
    # 表的名字:
    __tablename__ = 'user'

    # 表的结构:
    id = Column(String(20), primary_key=True)
    name = Column(String(20))
    age = Column(Integer)

    def __repr__(self):
        return 'User(id={id},name={name},age={age})'.format(id=self.id, name=self.name, age=self.age)


class SqlalchemyTestCase(unittest.TestCase):
    """docstring for SqlalchemyTestCase"""

    def stest_1(self):
        """init drop"""
        sql_opt = SqlalchemyOperation(DB_INFO)
        # sql_opt.drop_db()
        # sql_opt.init_db()

    def test_2(self):
        """测试创建表"""
        sql_opt = SqlalchemyOperation(DB_INFO)
        # 创建新User对象:
        new_user = User(id='7', name='ali', age=11)
        user1 = User(id='8', name='mary', age=12)
        user2 = User(id=1, name='bob', age=12)
        # 插入数据
        sql_opt.session.add(new_user)
        sql_opt.session.add_all([user2, user1])
        # 提交即保存到数据库:
        sql_opt.session.commit()

        # 更新数据
        sql_opt.session.query(User).filter(User.name == 'ali').update({'name': 'da'})
        # 删除数据
        sql_opt.session.query(User).filter(User.id == 1).delete()
        sql_opt.session.commit()
        # 查询数据
        ret = sql_opt.session.query(User).all()
        print(ret)
        sql_opt.session.close()


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(SqlalchemyTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
    pass
