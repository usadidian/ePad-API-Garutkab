from flask_restful import Resource, reqparse
from sqlalchemy import func, text
import datetime
import time

from config.database import db
from controller.tblUser import tblUser
from controller.vw_setoranhist import vw_setoranhist
from controller.vw_target import vw_target


class Transactions(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}
    def get(self, *args, **kwargs):
        """
                Get Transaction List
                ---
                tags:
                  - Transactions
                summary: Retrieve filtered tax payment transactions with pagination
                description: |
                  Returns a paginated list of tax payment transactions filtered by revenue account code, tax entity ID, and date range.
                  Supports date filtering, pagination, and sorting by payment date.
                security:
                  - ApiKeyAuth: []
                parameters:
                  - name: revenueAccountCode
                    in: query
                    type: string
                    required: false
                    description: Filter by revenue account code (KodeRekening)
                  - name: taxEntityId
                    in: query
                    type: string
                    required: false
                    description: Filter by taxpayer entity ID (ObyekBadanNo)
                  - name: startDate
                    in: query
                    type: string
                    format: date
                    required: false
                    description: Filter payments made after or on this date (YYYY-MM-DD)
                  - name: endDate
                    in: query
                    type: string
                    format: date
                    required: false
                    description: Filter payments made before or on this date (YYYY-MM-DD)
                  - name: page
                    in: query
                    type: integer
                    required: false
                    default: 1
                    description: Page number for pagination
                  - name: limit
                    in: query
                    type: integer
                    required: false
                    default: 10
                    description: Number of records per page
                responses:
                  200:
                    description: Paginated list of tax transactions
                    schema:
                      type: object
                      properties:
                        last_update:
                          type: string
                          format: date-time
                          example: "2025-05-25T12:30:00"
                          description: Last update timestamp from the most recent record
                        total_data:
                          type: integer
                          example: 120
                        total_page:
                          type: integer
                          example: 12
                        current_page:
                          type: integer
                          example: 1
                        last_page:
                          type: integer
                          example: 12
                        from_data:
                          type: integer
                          example: 1
                        to_data:
                          type: integer
                          example: 10
                        data:
                          type: array
                          items:
                            type: object
                            properties:
                              last_update:
                                type: string
                                format: date-time
                                example: "2025-05-25T12:30:00"
                              payment_code:
                                type: string
                                example: "SSPD20250525001"
                              tax_number:
                                type: string
                                example: "KH202504123"
                              entity_name:
                                type: string
                                example: "PT Sumber Rezeki"
                              tax_period:
                                type: string
                                example: "2025-04"
                              tax_amount:
                                type: number
                                format: float
                                example: 1000000.0
                              tax_fine:
                                type: number
                                format: float
                                example: 50000.0
                              pay_amount:
                                type: number
                                format: float
                                example: 1050000.0
                              diff_amount:
                                type: number
                                format: float
                                example: 50000.0
                              payment_date:
                                type: integer
                                format: unix
                                example: 1716600000
                  400:
                    description: Invalid date format
                  401:
                    description: Unauthorized (invalid or missing API key)
                """
        parser = reqparse.RequestParser()
        parser.add_argument('revenueAccountCode', type=str, location='args')
        parser.add_argument('taxEntityId', type=str, location='args')
        parser.add_argument('startDate', type=str, location='args')
        parser.add_argument('endDate', type=str, location='args')
        parser.add_argument('page', type=int, location='args', default=1)
        parser.add_argument('limit', type=int, location='args', default=10)
        args = parser.parse_args()

        query = db.session.query(
            vw_setoranhist.DateUpd.label("last_update"),
            vw_setoranhist.NoSSPD.label("payment_code"),
            vw_setoranhist.KohirID.label("tax_number"),
            vw_setoranhist.NamaBadan.label("entity_name"),
            func.substring(
                func.convert(text("varchar"), vw_setoranhist.MasaAkhir, 120), 1, 7
            ).label("tax_period"),
            vw_setoranhist.Pajak.label("tax_amount"),
            vw_setoranhist.Denda.label("tax_fine"),
            vw_setoranhist.JmlBayar.label("pay_amount"),
            (vw_setoranhist.JmlBayar - vw_setoranhist.Pajak).label("diff_amount"),
            vw_setoranhist.TglBayar.label("payment_date")
        ).join(
            vw_target,
            vw_setoranhist.UsahaBadan == vw_target.JenisPendapatanID
        )

        if args['revenueAccountCode']:
            query = query.filter(vw_target.KodeRekening == args['revenueAccountCode'])

        if args['taxEntityId']:
            query = query.filter(vw_setoranhist.ObyekBadanNo == args['taxEntityId'])

        if args['startDate']:
            try:
                start = datetime.datetime.strptime(args['startDate'], '%Y-%m-%d')
                query = query.filter(vw_setoranhist.TglBayar >= start)
            except ValueError:
                return {'message': 'Invalid startDate format, must be YYYY-MM-DD'}, 400

        if args['endDate']:
            try:
                end = datetime.datetime.strptime(args['endDate'], '%Y-%m-%d')
                query = query.filter(vw_setoranhist.TglBayar <= end)
            except ValueError:
                return {'message': 'Invalid endDate format, must be YYYY-MM-DD'}, 400

        # Pagination logic
        total_items = query.count()
        page = args['page']
        limit = args['limit']
        total_page = (total_items + limit - 1) // limit if total_items else 0
        last_page = total_page
        from_data = (page - 1) * limit + 1 if total_items > 0 else 0
        to_data = min(from_data + limit - 1, total_items) if total_items > 0 else 0

        query = query.order_by(vw_setoranhist.TglBayar.desc())
        items = query.offset((page - 1) * limit).limit(limit).all()

        # Format response data


        data = []
        last_update = None
        for item in items:
            payment_ts = int(time.mktime(item.payment_date.timetuple())) if item.payment_date else None
            data.append({
                "last_update": item.last_update,
                "payment_code": item.payment_code,
                "tax_number": item.tax_number,
                "entity_name": item.entity_name,
                "tax_period": item.tax_period,
                "tax_amount": float(item.tax_amount or 0),
                "tax_fine": float(item.tax_fine or 0),
                "pay_amount": float(item.pay_amount or 0),
                "diff_amount": float(item.diff_amount or 0),
                "payment_date": payment_ts
            })
        if items:
            last_update = items[0].last_update
        return {
            "last_update": last_update,
            "data": data,
            "total_data": total_items,
            "total_page": total_page,
            "current_page": page if total_items > 0 else 0,
            "last_page": last_page,
            "from_data": from_data,
            "to_data": to_data
        }, 200
