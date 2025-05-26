from flask_restful import Resource, reqparse
from sqlalchemy import func, and_, or_, cast, String
from flask import jsonify
from datetime import date

from config.database import db
from controller.tblUser import tblUser
from controller.vw_setoranhist import vw_setoranhist
from controller.vw_target import vw_target


class TaxEntities(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):
        """
                Tax Entities API
                ---
                tags:
                  - Tax Entities
                summary: Get tax objects/entities with unpaid bills
                description: Returns a paginated list of tax entities (businesses) filtered by account code, bill status, or search query.
                security:
                  - ApiKeyAuth: []
                parameters:
                  - name: revenueAccountCode
                    in: query
                    type: string
                    required: false
                    description: Filter by KodeRekening (account code)
                  - name: hasBill
                    in: query
                    type: boolean
                    required: false
                    description: Filter to show only entities with unpaid taxes (Pajak > 0)
                  - name: search
                    in: query
                    type: string
                    required: false
                    description: Search by tax number (SKP/SPTP) or business name
                  - name: page
                    in: query
                    type: integer
                    required: false
                    default: 1
                    description: Page number
                  - name: limit
                    in: query
                    type: integer
                    required: false
                    default: 10
                    description: Number of results per page
                responses:
                  200:
                    description: A paginated list of tax entities
                    schema:
                      type: object
                      properties:
                        data:
                          type: array
                          items:
                            type: object
                            properties:
                              tax_number:
                                type: integer
                                example: 123456
                              category:
                                type: string
                                example: "Pajak Restoran"
                              name:
                                type: string
                                example: "PT Maju Jaya"
                              address:
                                type: string
                                example: "Jl. Merdeka No.1"
                              last_tax_period:
                                type: string
                                example: "2025-04"
                              total_bill:
                                type: number
                                format: float
                                example: 500000.0
                              revenue_target:
                                type: number
                                format: float
                                example: 15000000.0
                        total_data:
                          type: integer
                          example: 25
                        total_page:
                          type: integer
                          example: 3
                        current_page:
                          type: integer
                          example: 1
                        last_page:
                          type: integer
                          example: 3
                        from_data:
                          type: integer
                          example: 1
                        to_data:
                          type: integer
                          example: 10
                  401:
                    description: Unauthorized (invalid or missing API key)
                """
        parser = reqparse.RequestParser()
        parser.add_argument('revenueAccountCode', type=str, location='args')
        parser.add_argument('hasBill', type=bool, location='args')
        parser.add_argument('search', type=str, location='args')
        parser.add_argument('page', type=int, location='args', default=1)
        parser.add_argument('limit', type=int, location='args', default=10)
        args = parser.parse_args()

        query = db.session.query(
            vw_setoranhist.KohirID.label('tax_number'),
            vw_setoranhist.NamaJenisPendapatan.label('category'),
            vw_setoranhist.NamaBadan.label('name'),
            vw_setoranhist.AlamatBadan.label('address'),
            func.max(vw_setoranhist.MasaAkhir).label('last_tax_period'),
            func.sum(vw_setoranhist.Pajak).label('total_bill'),
            vw_target.TargetPendapatan.label('revenue_target')
        ).outerjoin(
            vw_target,
            and_(
                vw_target.JenisPendapatanID == vw_setoranhist.UsahaBadan,
                vw_target.TahunPendapatan == date.today().year
            )
        )\
        .filter(vw_setoranhist.StatusBayar == None )

        # Filter: by KodeRekening
        if args['revenueAccountCode']:
            query = query.filter(vw_setoranhist.KodeRekening == args['revenueAccountCode'])

        # Filter: unpaid taxes (assuming "hasBill" means there is a bill, i.e., JmlBayar > 0)
        if args['hasBill'] is True:
            query = query.filter(vw_setoranhist.Pajak > 0)

        # Filter: search (name or tax_number/KohirID)
        if args['search']:
            search_term = f"%{args['search']}%"
            query = query.filter(or_(
                vw_setoranhist.NamaBadan.ilike(search_term),
                cast(vw_setoranhist.KohirID, String).ilike(search_term)
            ))

        query = query.group_by(
            vw_setoranhist.KohirID,
            vw_setoranhist.NamaJenisPendapatan,
            vw_setoranhist.NamaBadan,
            vw_setoranhist.AlamatBadan,
            vw_target.TargetPendapatan
        )
        # ORDER BY diperlukan untuk MSSQL OFFSET/FETCH
        query = query.order_by(vw_setoranhist.KohirID)

        # Pagination
        total_data = query.count()
        limit = args['limit']
        page = args['page']
        offset = (page - 1) * limit
        total_page = (total_data + limit - 1) // limit  # ceiling division
        last_page = total_page

        rows = query.offset(offset).limit(limit).all()

        result = []
        for row in rows:
            last_period_str = row.last_tax_period.strftime('%Y-%m') if row.last_tax_period else None
            result.append({
                "tax_number": row.tax_number,
                "category": row.category,
                "name": row.name,
                "address": row.address,
                "last_tax_period": last_period_str,
                "total_bill": float(row.total_bill or 0),
                "revenue_target": float(row.revenue_target or 0)
            })

        return jsonify({
            "data": result,
            "total_data": total_data,
            "total_page": total_page,
            "current_page": page,
            "last_page": last_page,
            "from_data": offset + 1 if total_data > 0 else 0,
            "to_data": offset + len(rows)
        })
