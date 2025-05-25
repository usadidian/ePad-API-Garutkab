from datetime import datetime, timedelta
from flask_restful import Resource, reqparse
from sqlalchemy import func, extract
from config.database import db
from controller.tblUser import tblUser
from controller.vw_setoranhist import vw_setoranhist
from controller.vw_target import vw_target


class RevenueSummary(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, *args, **kwargs):
        """
                Revenue Summary API
                ---
                tags:
                  - Revenue Summary
                parameters:
                  - name: date
                    in: query
                    type: string
                    required: true
                    format: date
                    description: Tanggal yang ingin diambil datanya (format YYYY-MM-DD)
                  - name: account_code
                    in: query
                    type: string
                    required: false
                    description: Kode rekening (opsional)
                security:
                  - ApiKeyAuth: []
                responses:
                  200:
                    description: Ringkasan penerimaan berhasil diambil
                    schema:
                      type: object
                      properties:
                        revenue_total:
                          type: number
                        revenue_target:
                          type: number
                        revenue_percentage:
                          type: number
                        revenue_day:
                          type: number
                        revenue_day_before:
                          type: number
                        revenue_week:
                          type: number
                        revenue_week_before:
                          type: number
                        revenue_month:
                          type: number
                        revenue_month_before:
                          type: number
                  400:
                    description: Format tanggal tidak valid
                  404:
                    description: Data tidak ditemukan
                """
        parser = reqparse.RequestParser()
        parser.add_argument('date', type=str, required=True,
                            help="Parameter 'date' wajib diisi (format YYYY-MM-DD)")
        parser.add_argument('account_code', type=str, required=False)
        args = parser.parse_args()

        try:
            target_date = datetime.strptime(args['date'], "%Y-%m-%d")
        except ValueError:
            return {"message": "Format tanggal tidak valid. Gunakan format YYYY-MM-DD"}, 400

        filters = [vw_setoranhist.TglBayar == target_date]
        if args['account_code']:
            filters.append(vw_setoranhist.KodeRekening == args['account_code'])

        revenue_total = db.session.query(func.coalesce(func.sum(vw_setoranhist.JmlBayar), 0)) \
            .filter(*filters).scalar()

        # Get target
        revenue_target = db.session.query(func.coalesce(func.sum(vw_target.TargetPendapatan), 0)) \
            .filter(
            vw_target.TahunPendapatan == str(target_date.year),
            *([vw_target.KodeRekening == args['account_code']] if args['account_code'] else [])
        ).scalar()

        # Percentage
        revenue_percentage = (revenue_total / revenue_target * 100) if revenue_target > 0 else 0

        # Day before
        revenue_day_before = db.session.query(func.coalesce(func.sum(vw_setoranhist.JmlBayar), 0)) \
            .filter(
            vw_setoranhist.TglBayar == (target_date - timedelta(days=1)),
            *([vw_setoranhist.KodeRekening == args['account_code']] if args['account_code'] else [])
        ).scalar()

        # Week
        revenue_week = db.session.query(func.coalesce(func.sum(vw_setoranhist.JmlBayar), 0)) \
            .filter(
            extract('week', vw_setoranhist.TglBayar) == target_date.isocalendar()[1],
            extract('year', vw_setoranhist.TglBayar) == target_date.year,
            *([vw_setoranhist.KodeRekening == args['account_code']] if args['account_code'] else [])
        ).scalar()

        # Week before
        previous_week = target_date - timedelta(days=7)
        revenue_week_before = db.session.query(func.coalesce(func.sum(vw_setoranhist.JmlBayar), 0)) \
            .filter(
            extract('week', vw_setoranhist.TglBayar) == previous_week.isocalendar()[1],
            extract('year', vw_setoranhist.TglBayar) == previous_week.year,
            *([vw_setoranhist.KodeRekening == args['account_code']] if args['account_code'] else [])
        ).scalar()

        # Month
        revenue_month = db.session.query(func.coalesce(func.sum(vw_setoranhist.JmlBayar), 0)) \
            .filter(
            extract('month', vw_setoranhist.TglBayar) == target_date.month,
            extract('year', vw_setoranhist.TglBayar) == target_date.year,
            *([vw_setoranhist.KodeRekening == args['account_code']] if args['account_code'] else [])
        ).scalar()

        # Month before
        prev_month = (target_date.replace(day=1) - timedelta(days=1))
        revenue_month_before = db.session.query(func.coalesce(func.sum(vw_setoranhist.JmlBayar), 0)) \
            .filter(
            extract('month', vw_setoranhist.TglBayar) == prev_month.month,
            extract('year', vw_setoranhist.TglBayar) == prev_month.year,
            *([vw_setoranhist.KodeRekening == args['account_code']] if args['account_code'] else [])
        ).scalar()

        # Return if no data
        if all(v == 0 for v in [revenue_total, revenue_day_before, revenue_week, revenue_week_before, revenue_month,
                                revenue_month_before]):
            return {"message": "No data found for the provided query parameters"}, 404

        return {
            # "message": "Revenue summary successfully loaded",
            "revenue_total": float(revenue_total),
            "revenue_target": float(revenue_target),
            "revenue_percentage": round(revenue_percentage, 2),
            "revenue_day": float(revenue_total),
            "revenue_day_before": float(revenue_day_before),
            "revenue_week": float(revenue_week),
            "revenue_week_before": float(revenue_week_before),
            "revenue_month": float(revenue_month),
            "revenue_month_before": float(revenue_month_before),
        }, 200