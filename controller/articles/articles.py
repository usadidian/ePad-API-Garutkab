from multiprocessing import Process
from pathlib import Path

import yagmail
from flask import request
from flask_restful import Resource, inputs
from sqlalchemy import desc, or_
from sqlalchemy_serializer import SerializerMixin
from config.helper import *
from config.api_message import success_reads, failed_reads, success_read, failed_read, success_reads_pagination, \
    success_create, failed_create, success_delete, failed_delete, success_update, failed_update
from config.database import db
from controller.task.task_bridge import GoToTaskUploadAvatar, GoToTaskUploadArticleImg, GoToTaskDeleteArticleImg
from controller.tblUser import tblUser


class ArticlesCategories(db.Model):
    __tablename__ = 'articlesCategories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    img = db.Column(db.String, nullable=True)
    icon = db.Column(db.String, nullable=True)

    articles = db.relationship("Articles", backref="articlesCategories", lazy="dynamic")

    def __init__(self, **kwargs):
        super(ArticlesCategories, self).__init__(**kwargs)

    def __repr__(self):
        return f"<ArticlesCategories {self.name}>"


class Articles(db.Model, SerializerMixin):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    id_articlesCategories = db.Column(db.Integer, db.ForeignKey('articlesCategories.id'), nullable=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    img = db.Column(db.String, nullable=True)
    video = db.Column(db.String, nullable=True)
    # doc = db.Column( db.String, nullable=True )
    isVideoFirst = db.Column(db.Boolean, nullable=True)
    view_count = db.Column(db.Integer, nullable=True)
    comment_count = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.TIMESTAMP, nullable=True, default=datetime.now())
    last_updated_date = db.Column(db.TIMESTAMP, nullable=True, default=datetime.now())
    created_by = db.Column(db.String, nullable=True)
    last_updated_by = db.Column(db.String, nullable=True)

    @property
    def categories_name(self):
        return self.articlesCategories.name


class ArticlesCategoriesList(Resource):
    # method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):
        try:
            select_data = ArticlesCategories.query.order_by(ArticlesCategories.name).all()
            result = []
            for row in select_data:
                result.append(toDict(row))
            return success_read(result)
        except Exception as e:
            print(e)
            return failed_reads({})


class ArticlesList(Resource):
    method_decorators = {'post': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int)
            parser.add_argument('length', type=int)
            parser.add_argument('sort', type=str)
            parser.add_argument('sort_dir', type=str, choices=('asc', 'desc'), help='diisi dengan asc atau desc')
            parser.add_argument('search', type=str)
            parser.add_argument('categories', type=int)
            args = parser.parse_args()
            select_query = db.session.query(Articles)

            # FILTERS
            if args['categories']:
                select_query = select_query.filter(
                    Articles.id_articlesCategories == args['categories']
                )

            # SEARCH
            if args['search'] and args['search'] != 'null':
                search = '%{0}%'.format(args['search'])
                select_query = select_query.filter(
                    or_(
                        Articles.title.ilike(search),
                        Articles.description.ilike(search),
                    )
                )

            # SORT
            if args['sort']:
                if args['sort_dir'] == "desc":
                    sort = getattr(Articles, args['sort']).desc()
                else:
                    sort = getattr(Articles, args['sort']).asc()
                select_query = select_query.order_by(sort)
            else:
                select_query = select_query.order_by(Articles.last_updated_date.desc())

            # PAGINATION
            page = args['page'] if args['page'] else 1
            length = args['length'] if args['length'] else 10
            lengthLimit = length if length < 101 else 100
            query_execute = select_query.paginate(page, lengthLimit)
            result = []
            for row in query_execute.items:
                result.append(toDict(row))
            return success_reads_pagination(query_execute, result)
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return failed_reads({})

    def post(self, *args, **kwargs):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('id_articlesCategories', type=int)
            parser.add_argument('title', type=str, required=True, help="Harus diisi")
            parser.add_argument('description', type=str)
            parser.add_argument('isVideoFirst', type=inputs.boolean)
            parser.add_argument('video', type=str)
            parser.add_argument( 'doc', type=str )
            args = parser.parse_args()
            isVideoFirst = bool(args['isVideoFirst'])
            if isVideoFirst and not args['video']:
                return "please input video url", 400
            if args['video'] and not isVideoFirst:
                isVideoFirst = True
            UserId = kwargs['claim']["UserId"]
            add_record = Articles(
                id_articlesCategories=args['id_articlesCategories'],
                title=args['title'],
                description=args['description'],
                video=args['video'],
                doc=args['doc'],
                isVideoFirst=isVideoFirst,
                created_by=kwargs['claim']["UID"],
                last_updated_by=kwargs['claim']["UID"],
            )
            db.session.add(add_record)
            db.session.commit()

            if add_record.id:
                # ////INCLUDE IMG
                files_img = request.files
                if files_img:
                    if not os.path.exists(f'./static/uploads/article_temp'):
                        os.makedirs(f'./static/uploads/article_temp')
                    folder_temp = f'./static/uploads/article_temp'

                    # add item img and upload
                    filenames = []

                    for img_row in files_img.items():
                        img_row_ok = img_row[1]
                        if img_row_ok.filename == '':
                            logger.info('file image dengan nama img wajib disertakan')
                        if img_row_ok:
                            new_filename = f"{add_record.id}.png"
                            img_row_ok.save(os.path.join(folder_temp, new_filename))
                            filenames.append(new_filename)
                    filenames_str = ','.join([str(elem) for elem in filenames])
                    # logger.info(filenames_str)
                    if filenames_str != '':
                        thread = Process(target=GoToTaskUploadArticleImg,
                                         args=(folder_temp, filenames_str, add_record.id, UserId, request.origin))
                        thread.daemon = True
                        thread.start()
            else:
                db.session.rollback()
            return success_create({})
        except Exception as e:
            db.session.rollback()
            print(e)
            return not failed_create({})


class ArticlesById(Resource):
    method_decorators = {'delete': [tblUser.auth_apikey_privilege], 'put': [tblUser.auth_apikey_privilege]}

    def delete(self, id, *args, **kwargs):
        try:
            check_header = Articles.query.filter_by(id=id)
            check = check_header.first()
            if check and check.img:
                thread = Process(target=GoToTaskDeleteArticleImg(check.img, request.origin))
                thread.daemon = True
                thread.start()
            check_header.delete()
            db.session.commit()
            if check_header:
                return success_delete({})
            else:
                db.session.rollback()
                return failed_delete({})
        except Exception as e:
            db.session.rollback()
            print(e)
            return failed_delete({})


    def put(self, id, *args, **kwargs):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('id_articlesCategories', type=int)
            parser.add_argument('title', type=str, required=True, help="Harus diisi")
            parser.add_argument('description', type=str)
            parser.add_argument('isVideoFirst', type=inputs.boolean)
            parser.add_argument('video', type=str)
            args = parser.parse_args()
            if args:
                select_query = Articles.query.filter_by(id=id).first()
                if args['id_articlesCategories']:
                    select_query.id_articlesCategories = args['id_articlesCategories']
                if args['title']:
                    select_query.title = args['title']
                if args['description']:
                    select_query.description = args['description']
                if args['isVideoFirst']:
                    select_query.isVideoFirst = args['isVideoFirst']
                if args['video']:
                    select_query.video = args['video']
                    if select_query.img:
                        thread = Process(target=GoToTaskDeleteArticleImg(select_query.img, request.origin))
                        thread.daemon = True
                        thread.start()
                    select_query.img = None
                    # select_query.isVideoFirst = True
                # else:
                #     select_query.isVideoFirst = False
                select_query.last_updated_by = kwargs['claim']["UID"]
                select_query.last_updated_date = datetime.now()
                # ////INCLUDE IMG
                files_img = request.files
                if files_img:
                    if not os.path.exists(f'./static/uploads/article_temp'):
                        os.makedirs(f'./static/uploads/article_temp')
                    folder_temp = f'./static/uploads/article_temp'

                    # add item img and upload
                    filenames = []

                    for img_row in files_img.items():
                        img_row_ok = img_row[1]
                        if img_row_ok.filename == '':
                            logger.info('file image dengan nama img wajib disertakan')
                        if img_row_ok:
                            new_filename = f"{id}.png"
                            img_row_ok.save(os.path.join(folder_temp, new_filename))
                            filenames.append(new_filename)
                    filenames_str = ','.join([str(elem) for elem in filenames])
                    # logger.info(filenames_str)
                    if filenames_str != '':
                        thread = Process(target=GoToTaskUploadArticleImg,
                                         args=(folder_temp, filenames_str, id,
                                               kwargs['claim']['UserId'], request.origin))
                        thread.daemon = True
                        thread.start()

                db.session.commit()
            return success_update({})
        except Exception as e:
            logger.error(e)
            return failed_update({})