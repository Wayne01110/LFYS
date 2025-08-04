import requests
from pandas._libs.parsers import defaultdict
from rest_framework import status
from rest_framework.views import APIView

from dvadmin.utils.json_response import DetailResponse


class LFProjectPackageDoctorView(APIView):
    permission_classes = []
    """
        add by Wayne 2025-06-20  项目&套餐排行AND医生划扣排行
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

            # 第三步：712执行业绩结算明细
            report_712 = {
                "current": 1,
                "limit": 50000,
                "serviceTimeStart": start_time,
                "serviceTimeEnd": end_time
            }

            report_response_712 = requests.post(
                url="https://lfyisheng.hospital.realmerit.com.cn/api/report/v1/executivePerformanceDetail/report",
                json=report_712,
                headers={
                    "Content-Type": "application/json",
                    "authorization": token
                }
            )

            if report_response.status_code == 200 and report_response_712.status_code == 200:
                # 出纳结算单
                # === 项目&套餐排行 ===
                report_json = report_response.json()
                records = report_json.get('data', {}).get('page', {}).get('records', [])
                project_achievements = defaultdict(float)
                package_achievements = defaultdict(float)

                for record in records:
                    # projectActualMoney    项目本次实付/实退
                    # projectThreeName      项目（三级分类）
                    # num                   数量
                    # consumerCustomerType  消费时客户类别
                    # billingUserName       原订单开单人
                    # productTwoName        产品（二级分类）
                    # departmentName        科室（一级分类）
                    # achievement           本次结算业绩
                    # vipNum                会员号
                    project = record.get('projectThreeName')  # 项目（三级分类）
                    package = record.get('packageName')  # 所属套餐
                    vip_num = str(record.get('vipNum'))  # 会员号
                    achievement = float(record.get('achievement') or 0.0)  # 本次结算业绩
                    if project:
                        project_achievements[project] += achievement
                    if package:
                        package_achievements[package] += achievement

                # 712执行业绩结算明细
                # === 医生划扣数量排行 + 人次 ===
                report_712_json = report_response_712.json()
                records_712 = report_712_json.get('data', {}).get('records', [])
                doctor_deduct_count = defaultdict(int)  # 医生 -> 总划扣数量
                doctor_deduct_times = defaultdict(int)  # 医生 -> 划扣记录条数（人次）

                for r in records_712:
                    role_name = r.get("serviceUserRoleNames")
                    service_name = r.get("serviceUserName")
                    number_of_time = int(r.get("numberOfTime") or 0)

                    if role_name in ["医生-CC", "院长-CC"] and service_name:
                        doctor_deduct_count[service_name] += number_of_time
                        doctor_deduct_times[service_name] += 1  # 每条记录为一次人次

                # 排序结果
                project_rank = sorted(
                    [{"name": name, "achievement": round(value, 2)} for name, value in project_achievements.items()],
                    key=lambda x: x["achievement"], reverse=True
                )

                package_rank = sorted(
                    [{"name": name, "achievement": round(value, 2)} for name, value in package_achievements.items()],
                    key=lambda x: x["achievement"], reverse=True
                )

                doctor_sorted = sorted([
                    {
                        "name": name,
                        "划扣数量": doctor_deduct_count[name],
                        "划扣人次": doctor_deduct_times[name]
                    }
                    for name in doctor_deduct_count
                ], key=lambda x: x["划扣数量"], reverse=True)

                return DetailResponse(data={
                    "项目排行": project_rank,
                    "套餐排行": package_rank,
                    "医生划扣数量排行": doctor_sorted,
                }, status=status.HTTP_200_OK)
            else:
                return DetailResponse({
                    "error": "数据查询失败",
                    "cashier_status": report_response.status_code,
                    "performance_status": report_response_712.status_code
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return DetailResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
