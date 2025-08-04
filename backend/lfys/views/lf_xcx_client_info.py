import requests
from pandas._libs.parsers import defaultdict
from rest_framework import status
from rest_framework.views import APIView

from dvadmin.utils.json_response import DetailResponse


class LFXcxClientInfoView(APIView):
    permission_classes = []

    """
        add by Wayne 2025-06-07  小程序客户积分统计
    """

    def post(self, request):
        # ⏳ 获取绑定日期区间
        start_time = request.data.get('bindDateStart')
        end_time = request.data.get('bindDateEnd')

        # 🔐 登录获取 token
        login_payload = {
            "account": "18188889999",
            "password": "H8hoo1gJdWXnbetiQgF8r9DWjTdnLxXUREoVdMZvL5+aEGCHPfXVB5WUhkYy7VJ6kvz+m9HBut4SP7oksBwGIp9Au2nUKku3+QOD/C54lTh/+dW4MyOE1nCRz/3pBu87/PhFpGX43MdIOSY+qCaCbnyl3QLO4LwtKky60VhW844=",
            "hospitalKey": "lfys4123",
            "tenantId": "0",
            "type": 1,
            "mac": "",
            "loginType": "PC_WEB"
        }

        try:
            login_response = requests.post(
                url="https://lfyisheng.hospital.realmerit.com.cn/api/v1/login",
                json=login_payload,
                headers={"Content-Type": "application/json"}
            )

            if login_response.status_code != 200:
                return DetailResponse({"error": "登录失败", "details": login_response.json()}, status=status.HTTP_400_BAD_REQUEST)

            token = login_response.json().get("data", {}).get("user", {}).get("token")
            if not token:
                return DetailResponse({"error": "登录响应中未获取到 token"}, status=status.HTTP_400_BAD_REQUEST)

            # 👥 获取客户列表
            report_payload = {
                "bindDateStart": start_time,
                "bindDateEnd": end_time,
                "size": 20000,
                "current": 1,
                "crossFlag": 1,
                "isGroup": True
            }

            report_response = requests.post(
                url="https://lfyisheng.hospital.realmerit.com.cn/api/v1/scrm/customer/scrmCustomerList",
                json=report_payload,
                headers={
                    "Content-Type": "application/json",
                    "authorization": token
                }
            )

            if report_response.status_code == 200:
                records = report_response.json().get('data', {}).get('list', [])

                # ✅ 集团层统计字段
                group_total_integral = 0
                group_total_customers = 0
                group_member_level_count = defaultdict(int)
                group_member_level_integral = defaultdict(int)

                # ✅ 门店层结构：{ 门店: {...} }
                store_data = {}

                for record in records:
                    tenant_name = record.get('tenantName', '').strip() or '未知门店'
                    integral = int(record.get('integral') or 0)
                    member_level = record.get('memberLevelName', '未知等级')

                    # 📊 集团统计累计
                    group_total_integral += integral
                    group_total_customers += 1
                    group_member_level_count[member_level] += 1
                    group_member_level_integral[member_level] += integral

                    # 📊 门店初始化
                    if tenant_name not in store_data:
                        store_data[tenant_name] = {
                            "totalIntegral": 0,
                            "totalCustomers": 0,
                            "memberLevelCount": defaultdict(int),
                            "memberLevelIntegral": defaultdict(int)
                        }

                    # 📊 门店累计
                    store_data[tenant_name]["totalIntegral"] += integral
                    store_data[tenant_name]["totalCustomers"] += 1
                    store_data[tenant_name]["memberLevelCount"][member_level] += 1
                    store_data[tenant_name]["memberLevelIntegral"][member_level] += integral

                # ✅ 输出构造

                group_summary = {
                    "totalIntegral": group_total_integral,                      # 全集团积分总和
                    "totalCustomers": group_total_customers,                   # 全集团客户总数
                    "memberLevelCount": dict(group_member_level_count),        # 各会员等级人数
                    "memberLevelIntegral": dict(group_member_level_integral)   # 各会员等级积分总和
                }

                store_summary = []
                for tenant_name, data in store_data.items():
                    store_summary.append({
                        "tenantName": tenant_name,                                      # 门店名称
                        "totalIntegral": data["totalIntegral"],                        # 积分总和
                        "totalCustomers": data["totalCustomers"],                      # 客户总数
                        "memberLevelCount": dict(data["memberLevelCount"]),            # 各等级人数
                        "memberLevelIntegral": dict(data["memberLevelIntegral"])       # 各等级积分
                    })

                output = {
                    "groupSummary": group_summary,
                    "storeSummary": store_summary
                }

                return DetailResponse(data=output, status=status.HTTP_200_OK)

            else:
                return DetailResponse({
                    "error": "客户信息查询失败",
                    "details": report_response.json()
                }, status=report_response.status_code)

        except Exception as e:
            return DetailResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)