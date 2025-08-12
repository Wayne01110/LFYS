import requests
from rest_framework import status
from rest_framework.views import APIView
from collections import defaultdict
from dvadmin.utils.json_response import DetailResponse


class LFProjectDealRankView(APIView):
    permission_classes = []
    """
        add by Wayne 2025-04-14  咨询师项目业绩排行
    """

    def post(self, request):
        # 获取前端参数
        start_time = request.data.get('startChargeTime')
        end_time = request.data.get('endChargeTime')
        # 登录接口 payload
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
            # 第一步：调用登录接口获取 token
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
            # 第二步：请求出纳结算单接口
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
            if report_response.status_code == 200:
                report_json = report_response.json()
                records = report_json.get('data', {}).get('page', {}).get('records', [])
                result = defaultdict(lambda: {
                    '初复诊': defaultdict(lambda: {'成交人次': 0, '结算业绩': 0.0}),
                    '老客': defaultdict(lambda: {'成交人次': 0, '结算业绩': 0.0}),
                    '产品列表': set(),
                    '项目列表': set()
                })
                # projectActualMoney    项目本次实付/实退
                # projectThreeName      项目（三级分类）
                # num                   数量
                # consumerCustomerType  消费时客户类别
                # billingUserName       原订单开单人
                # productTwoName        产品（二级分类）
                # departmentName        科室（一级分类）
                # achievement           本次结算业绩
                # vipNum                会员号
                for record in records:
                    customer_type = record.get('consumerCustomerType', '').strip()  # 消费时客户类别
                    project = record.get('projectThreeName')  # 项目（三级分类）
                    product = record.get('productTwoName')  # 产品（二级分类）
                    depart = record.get('deptOneName')  # 科室（一级分类）
                    user = record.get('billingUserName')  # 原订单开单人
                    # money = float(record.get('projectActualMoney') or 0.0)        # 项目本次实付/实退
                    vip_num = str(record.get('vipNum'))  # 会员号
                    achievement = float(record.get('achievement') or 0.0)  # 本次结算业绩
                    if depart in ['禁用', '药品-CC', '商品-CC', '耗材-CC']:
                        continue
                    if not depart or not product or not user:
                        continue
                    # 初诊 + 复诊 + 其他 = 初复诊
                    if customer_type in ['初诊', '复诊', '其他']:
                        category = '初复诊'
                    # 老客人 + 空 = 老客
                    elif customer_type in ['老客人', '']:
                        category = '老客'
                    else:
                        continue
                    # 科室 - 产品
                    # key = f"{depart} - {product}"
                    key = f"{depart}"
                    result[key][category][user]['成交人次'] += 1
                    result[key][category][user]['结算业绩'] += achievement
                    if product:
                        result[key]['产品列表'].add(product)
                    if project:
                        result[key]['项目列表'].add(project)

                # 构建输出
                output = {}
                for dept_name, dept_data in result.items():
                    output[dept_name] = {
                        '初复诊': {},
                        '老客': {},
                        '产品列表': list(dept_data['产品列表']),
                        '项目列表': list(dept_data['项目列表']),
                    }

                    for category in ['初复诊', '老客']:
                        user_stats = dept_data[category]
                        sorted_user_data = dict(
                            sorted(user_stats.items(), key=lambda x: x[1]['结算业绩'], reverse=True)
                        )
                        output[dept_name][category] = sorted_user_data

                return DetailResponse(data=output, status=status.HTTP_200_OK)
            else:
                return DetailResponse({
                    "error": "出纳结算单查询失败",
                    "details": report_response.json()
                }, status=report_response.status_code)
        except Exception as e:
            return DetailResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
