from datetime import date
from flask import jsonify
from flask_restful import Resource
from sqlalchemy import func, cast, Date
from config.database import db
from controller.tblUser import tblUser
from controller.vw_setoranhist import vw_setoranhist
from controller.vw_target import vw_target


class RevenueCategories(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):
        """
                Revenue Categories API
                ---
                tags:
                  - Revenue Categories
                summary: Get revenue grouped by account/category
                description: Returns revenue summary per category (KodeRekening) including today, total, target, and last update.
                security:
                  - ApiKeyAuth: []
                responses:
                  200:
                    description: A list of revenue data by category
                    schema:
                      type: array
                      items:
                        type: object
                        properties:
                          account_code:
                            type: string
                            example: "4.1.1.01.01"
                          category_name:
                            type: string
                            example: "Pajak Hotel"
                          revenue_total:
                            type: number
                            format: float
                            example: 50000000.0
                          revenue_target:
                            type: number
                            format: float
                            example: 100000000.0
                          revenue_percentage:
                            type: number
                            format: float
                            example: 50.0
                          revenue_today:
                            type: number
                            format: float
                            example: 2500000.0
                          last_update:
                            type: integer
                            format: int64
                            example: 1716603600
                  401:
                    description: Unauthorized (invalid or missing API key)
                """
        today = date.today()
        current_year = today.year

        # Subquery untuk revenue_today per KodeRekening
        revenue_today_subquery = (
            db.session.query(
                vw_setoranhist.UsahaBadan.label('UsahaBadan'),
                vw_setoranhist.KodeRekening.label('KodeRekening'),
                func.sum(vw_setoranhist.JmlBayar).label('revenue_today')
            )
            .filter(cast(vw_setoranhist.TglBayar, Date) == today)
            .filter(vw_setoranhist.StatusBayar != None)
            .group_by(vw_setoranhist.UsahaBadan, vw_setoranhist.KodeRekening)
        ).subquery()

        # Subquery target tahunan per KodeRekening dari vw_target
        target_subquery = (
            db.session.query(
                vw_target.JenisPendapatanID.label('JenisPendapatanID'),
                vw_target.KodeRekening.label('KodeRekening'),
                vw_target.TargetPendapatan.label('revenue_target')
            )
            .filter(vw_target.TahunPendapatan == current_year)
        ).subquery()

        # Query utama
        rows = (
            db.session.query(
                vw_setoranhist.KodeRekening,
                vw_setoranhist.NamaJenisPendapatan,
                func.sum(vw_setoranhist.JmlBayar).label('revenue_total'),
                func.max(vw_setoranhist.TglBayar).label('last_update'),
                revenue_today_subquery.c.revenue_today,
                target_subquery.c.revenue_target
            )
            .outerjoin(revenue_today_subquery, vw_setoranhist.KodeRekening == revenue_today_subquery.c.KodeRekening)
            .outerjoin(target_subquery, vw_setoranhist.UsahaBadan == target_subquery.c.JenisPendapatanID)
            .filter(vw_setoranhist.StatusBayar != None)
            .group_by(
                vw_setoranhist.UsahaBadan,
                vw_setoranhist.KodeRekening,
                vw_setoranhist.NamaJenisPendapatan,
                revenue_today_subquery.c.revenue_today,
                target_subquery.c.JenisPendapatanID,
                target_subquery.c.revenue_target
            )
            .order_by(vw_setoranhist.KodeRekening)
        )

        result = []
        for row in rows:
            revenue_total = float(row.revenue_total or 0)
            revenue_target = float(row.revenue_target or 0)
            revenue_today = float(row.revenue_today or 0)

            revenue_percentage = round((revenue_total / revenue_target * 100), 2) if revenue_target > 0 else 0.0

            result.append({
                "account_code": row.KodeRekening,
                "category_name": row.NamaJenisPendapatan,
                "revenue_total": revenue_total,
                "revenue_target": revenue_target,
                "revenue_percentage": revenue_percentage,
                "revenue_today": revenue_today,
                "last_update": int(row.last_update.timestamp()) if row.last_update else None
            })

        return jsonify(result)