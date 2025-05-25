from datetime import datetime, timedelta
from flask import jsonify, session
from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy_serializer import SerializerMixin
from config.api_message import success_read, failed_read, success_update, failed_update, success_delete, failed_delete, \
    success_reads_pagination, success_reads
from config.database import db
from controller.tblUser import tblUser


# class vw_menu(db.Model, SerializerMixin):
# __tablename__ = 'vw_menu'
# SiteID = db.Column(db.Integer, primary_key=True)
# code_group = db.Column(db.String, nullable=False)
# flag_program = db.Column(db.String, nullable=False)
# code_fungsi = db.Column(db.String, nullable=False)
# MenuID = db.Column(db.Integer, nullable=False)
# code_parent = db.Column(db.Integer, nullable=False)
# description = db.Column(db.String, nullable=False)


class ListAll(Resource):

    # method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):
        try:
            query = db.session.execute("""SELECT 
            MenuID,
            (case when code_parent <> '' then '' else 
            ' &#160; ' end) + 
            (case when '~/' + [file_name] = '~/pembukuan/CetRegister.aspx' or '~/' + [file_name] = '~/pembukuan/CetRegister.aspx?' 
            then '<font color=#000000>' + [description] + '</font>' else (case when MenuID = (select distinct convert(varchar,code_parent) 
            from vw_menu m where code_group = 'ADM' 
            and ('~/' + [file_name] = '~/pembukuan/CetRegister.aspx' or '~/' + [file_name] = '~/pembukuan/CetRegister.aspx?')) 
            then '<b><font color=#000000>' else '' end) + [description] + (case when MenuID = (select distinct convert(varchar,code_parent) 
            from vw_menu m where code_group = 'ADM' 
            and ('~/' + [file_name] = '~/pembukuan/CetRegister.aspx' or '~/' + [file_name] = '~/pembukuan/CetRegister.aspx?')) 
            then '</b></font>' else '' end) end) + (case when code_parent <> '' 
            then '' else ' &#160; ' end) AS [Text],[file_name] AS [Description],
            (case when code_parent = '' then null else convert(int,code_parent) end) AS ParentID FROM vw_menu 
            WHERE code_group = 'ADM'""")
            result = []
            for row in query:
                d = {}
                for key in row.keys():
                    d[key] = getattr(row, key)
                result.append(d)
            return success_read(result)
        except Exception as e:
            print(e)
            return failed_read({})