from collections import defaultdict
from rest_framework.views import APIView
from rest_framework import status
from dvadmin.utils.json_response import DetailResponse  # 你原项目中的返回类
import requests


class LFProjectDealRankView(APIView):
    permission_classes = []

    """
        add by Wayne 2025-04-14  咨询师项目销售排行
    """

    def post(self, request):
        start_time = request.data.get('startChargeTime')
        end_time = request.data.get('endChargeTime')

        login_payload = {
            "account": "18188889999",
            "password": "PGHFbsn1XxiZ+qe0+uQBHSVaGtokdLuYMpoZbb2UUWakOT4FxiO39iBtovzfGi6TpK6kDbkYwaOTRdr2BMbDhMAiyrJwdgtj9sjYy6RYKyLTDpkBPQe0f4sgkejnQ9Go2MDXlQD1rMlwtzlBVIuZYMvx96Zd0Kb7oHoQEuypTBY=",
            "hospitalKey": "lfys4123",
            "tenantId": "0",
            "type": 1,
            "mac": "",
            "loginType": "PC_WEB"
        }

        try:
            # 登录获取 token
            login_response = requests.post(
                url="https://lfyisheng.hospital.realmerit.com.cn/api/v1/login",
                json=login_payload,
                headers={"Content-Type": "application/json"}
            )
            if login_response.status_code != 200:
                return DetailResponse({"error": "登录失败", "details": login_response.json()},
                                      status=status.HTTP_400_BAD_REQUEST)

            res_json = login_response.json()
            token = res_json.get("data", {}).get("user", {}).get("token")
            if not token:
                return DetailResponse({"error": "登录响应中未获取到 token"}, status=status.HTTP_400_BAD_REQUEST)

            # 查询报表数据
            report_payload = {
                "startChargeTime": start_time,
                "endChargeTime": end_time,
                "isQueryProject": False,
                "isQueryMaterial": False,
                "isQueryBalance": False,
                "isQueryEquityCard": False,
                "isQueryAnnualCard": False,
                "isQueryOnceCard": False,
                "isQueryDeposit": False,
                "tenantIds": [],
                "page": 1,
                "isPreReport": False,
                "size": 50000
            }

            report_response = requests.post(
                url="https://lfyisheng.hospital.realmerit.com.cn/api/v1/payment/cashier/settlement/report",
                json=report_payload,
                headers={
                    "Content-Type": "application/json",
                    "authorization": token
                }
            )
        except Exception as e:
            return DetailResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if report_response.status_code == 200:
            report_json = report_response.json()
            records = report_json.get('data', {}).get('page', {}).get('records', [])

            result = defaultdict(lambda: {
                '初复诊': defaultdict(float),
                '老客': defaultdict(float)
            })

            for record in records:
                customer_type = (record.get('consumerCustomerType') or '').strip()
                project = record.get('projectThreeName')
                user = record.get('billingUserName')
                money = float(record.get('projectActualMoney') or 0.0)

                if not project or not user:
                    continue

                # 判断分类
                if customer_type in ['初诊', '复诊', '其他']:
                    category = '初复诊'
                elif customer_type in ['老客人', '']:
                    category = '老客'
                else:
                    continue  # 其他类型忽略

                result[project][category][user] += money

            # 排序每个项目内的两类排行
            output = {}
            for project, category_data in result.items():
                output[project] = {}
                for category, user_data in category_data.items():
                    sorted_user_data = dict(sorted(user_data.items(), key=lambda x: x[1], reverse=True))
                    output[project][category] = sorted_user_data

            return DetailResponse(data=output, status=status.HTTP_200_OK)


