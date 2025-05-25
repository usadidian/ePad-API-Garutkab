from flask_restful import Resource, reqparse
from flask import request
from datetime import datetime, timedelta
from sqlalchemy import extract, func

from config.database import db
from controller.tblUser import tblUser
from controller.vw_setoranhist import vw_setoranhist
from controller.vw_target import vw_target


class RevenueLogType(Resource):
    method_decorators = {'get': [tblUser.auth_apikey_privilege]}

    def get(self, logType, *args, **kwargs):
        """
                Revenue Log Summary
                ---
                tags:
                  - Revenue Log Type
                summary: Get revenue summary logs by type (daily, weekly, monthly, quarterly, yearly)
                description: |
                  Returns an array of revenue collection summaries based on the specified log type and optional revenue account code.
                  Each entry contains total revenue, target revenue, and achievement percentage for that period.
                security:
                  - ApiKeyAuth: []
                parameters:
                  - name: logType
                    in: path
                    type: string
                    required: true
                    enum: [daily, weekly, monthly, quarterly, yearly]
                    description: The type of log summary to retrieve.
                  - name: limit
                    in: query
                    type: integer
                    required: false
                    default: 10
                    description: Number of entries to retrieve (e.g. last 10 periods)
                  - name: revenueAccountCode
                    in: query
                    type: string
                    required: false
                    description: Filter by specific KodeRekening (revenue account code)
                responses:
                  200:
                    description: List of revenue logs for the specified log type
                    schema:
                      type: array
                      items:
                        type: object
                        properties:
                          label:
                            type: string
                            example: "2025-05-24"
                            description: Label representing the period (date, week, month, etc.)
                          revenue_total:
                            type: number
                            format: float
                            example: 12000000.0
                          revenue_target:
                            type: number
                            format: float
                            example: 15000000.0
                          revenue_percentage:
                            type: number
                            format: float
                            example: 80.0
                  400:
                    description: Invalid logType provided
                  401:
                    description: Unauthorized (invalid or missing API key)
                """
        parser = reqparse.RequestParser()
        parser.add_argument('limit', type=int, default=10)
        parser.add_argument('revenueAccountCode', type=str, required=False)
        args = parser.parse_args()

        revenue_logs = []
        today = datetime.today()

        for i in range(args['limit']):
            if logType == 'daily':
                date = today - timedelta(days=i)
                label = date.strftime('%Y-%m-%d')

                filters = [vw_setoranhist.TglBayar == date]
                if args['revenueAccountCode']:
                    filters.append(vw_setoranhist.KodeRekening == args['revenueAccountCode'])

                revenue_total = db.session.query(func.coalesce(func.sum(vw_setoranhist.JmlBayar), 0)) \
                    .filter(*filters).scalar()

                revenue_target = db.session.query(func.coalesce(func.sum(vw_target.TargetPendapatan), 0)) \
                    .filter(
                        vw_target.TahunPendapatan == str(date.year),
                        *( [vw_target.KodeRekening == args['revenueAccountCode']] if args['revenueAccountCode'] else [] )
                    ).scalar()

            elif logType == 'monthly':
                year = today.year
                month = today.month - i
                while month <= 0:
                    month += 12
                    year -= 1
                label = f"{year}-{month:02d}"

                filters = [
                    extract('month', vw_setoranhist.TglBayar) == month,
                    extract('year', vw_setoranhist.TglBayar) == year
                ]
                if args['revenueAccountCode']:
                    filters.append(vw_setoranhist.KodeRekening == args['revenueAccountCode'])

                revenue_total = db.session.query(func.coalesce(func.sum(vw_setoranhist.JmlBayar), 0)) \
                    .filter(*filters).scalar()

                revenue_target = db.session.query(func.coalesce(func.sum(vw_target.TargetPendapatan), 0)) \
                    .filter(
                        vw_target.TahunPendapatan == str(year),
                        *( [vw_target.KodeRekening == args['revenueAccountCode']] if args['revenueAccountCode'] else [] )
                    ).scalar()

            elif logType == 'yearly':
                year = today.year - i
                label = str(year)

                filters = [extract('year', vw_setoranhist.TglBayar) == year]
                if args['revenueAccountCode']:
                    filters.append(vw_setoranhist.KodeRekening == args['revenueAccountCode'])

                revenue_total = db.session.query(func.coalesce(func.sum(vw_setoranhist.JmlBayar), 0)) \
                    .filter(*filters).scalar()

                revenue_target = db.session.query(func.coalesce(func.sum(vw_target.TargetPendapatan), 0)) \
                    .filter(
                        vw_target.TahunPendapatan == str(year),
                        *( [vw_target.KodeRekening == args['revenueAccountCode']] if args['revenueAccountCode'] else [] )
                    ).scalar()

            elif logType == 'weekly':
                week_date = today - timedelta(weeks=i)
                week = week_date.isocalendar()[1]
                year = week_date.year
                label = f"{year}-W{week}"

                filters = [
                    extract('week', vw_setoranhist.TglBayar) == week,
                    extract('year', vw_setoranhist.TglBayar) == year
                ]
                if args['revenueAccountCode']:
                    filters.append(vw_setoranhist.KodeRekening == args['revenueAccountCode'])

                revenue_total = db.session.query(func.coalesce(func.sum(vw_setoranhist.JmlBayar), 0)) \
                    .filter(*filters).scalar()

                revenue_target = db.session.query(func.coalesce(func.sum(vw_target.TargetPendapatan), 0)) \
                    .filter(
                        vw_target.TahunPendapatan == str(year),
                        *( [vw_target.KodeRekening == args['revenueAccountCode']] if args['revenueAccountCode'] else [] )
                    ).scalar()

            elif logType == 'quarterly':
                month_now = today.month
                quarter_now = (month_now - 1) // 3 + 1
                quarter = quarter_now - i
                year = today.year
                while quarter <= 0:
                    quarter += 4
                    year -= 1
                label = f"{year}-Q{quarter}"

                # Hitung bulan dalam kuartal
                month_start = (quarter - 1) * 3 + 1
                month_end = month_start + 2

                filters = [
                    extract('month', vw_setoranhist.TglBayar).between(month_start, month_end),
                    extract('year', vw_setoranhist.TglBayar) == year
                ]
                if args['revenueAccountCode']:
                    filters.append(vw_setoranhist.KodeRekening == args['revenueAccountCode'])

                revenue_total = db.session.query(func.coalesce(func.sum(vw_setoranhist.JmlBayar), 0)) \
                    .filter(*filters).scalar()

                revenue_target = db.session.query(func.coalesce(func.sum(vw_target.TargetPendapatan), 0)) \
                    .filter(
                        vw_target.TahunPendapatan == str(year),
                        *( [vw_target.KodeRekening == args['revenueAccountCode']] if args['revenueAccountCode'] else [] )
                    ).scalar()
            else:
                return {"message": f"logType '{logType}' tidak dikenali. Gunakan salah satu dari: daily, weekly, monthly, quarterly, yearly"}, 400

            revenue_percentage = round((revenue_total / revenue_target * 100), 2) if revenue_target > 0 else 0

            revenue_logs.append({
                "label": label,
                "revenue_total": float(revenue_total),
                "revenue_target": float(revenue_target),
                "revenue_percentage": revenue_percentage
            })

        return revenue_logs, 200
