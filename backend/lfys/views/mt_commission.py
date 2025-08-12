import re

import pandas as pd
from rest_framework.views import APIView
from rest_framework import status
from dvadmin.utils.json_response import DetailResponse


class MTCommissionView(APIView):
    permission_classes = []

    """
    add by Wayne 2025-08-05  美团佣金表
    """

    def post(self, request):
        files = request.FILES.getlist('files')
        if not files:
            return DetailResponse({'error': '请上传文件'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 识别文件
            inflow_file = detail_file = consult_file = None
            for file in files:
                if '预付订单' in file.name:
                    inflow_file = file
                elif '团购收益明细' in file.name:
                    detail_file = file
                elif '门店明细' in file.name:
                    consult_file = file

            if not inflow_file:
                return DetailResponse({'error': '未找到包含“预付订单”的文件'}, status=status.HTTP_400_BAD_REQUEST)

            standard_amount_config = {
                '靓范医生医美连锁（净月院区）': {'daily_amount': 6000, 'days': 10},
                '靓范医生医美连锁（欧亚新生活院区）': {'daily_amount': 12000, 'days': 10},
                '靓范医生医美连锁（松北万象汇院区）': {'daily_amount': 7000, 'days': 10},
                '靓范医生医美连锁（万象城院区）': {'daily_amount': 8000, 'days': 10},
                '靓范医生医美连锁（远大购物中心院区）': {'daily_amount': 6000, 'days': 10},
                '靓范医生医美连锁（呼市万象城院区）': {'daily_amount': 6000, 'days': 10},
                '靓范医生医美连锁（郑东万象城院区）': {'daily_amount': 6000, 'days': 10},
            }

            def to_int(value):
                try:
                    return int(round(float(value)))
                except:
                    return 0

            # 统一括号格式：半角()转全角（）并去首尾空格
            def to_full_width_brackets(s):
                if not isinstance(s, str):
                    return s
                return s.replace('(', '（').replace(')', '）').strip()

            inflow_df = pd.read_excel(inflow_file)
            detail_df = pd.read_excel(detail_file, header=1) if detail_file else pd.DataFrame()
            consult_df = pd.read_excel(consult_file) if consult_file else pd.DataFrame()

            if not detail_df.empty:
                detail_df['消费门店'] = detail_df['消费门店'].map(to_full_width_brackets)

            # 统一映射消费门店名到标准门店名
            standard_stores = list(standard_amount_config.keys())
            def map_to_standard_store(name):
                if not isinstance(name, str):
                    return name
                for std_name in standard_stores:
                    if std_name in name or name in std_name:
                        return std_name
                return name

            detail_df['消费门店'] = detail_df['消费门店'].apply(map_to_standard_store)

            # 替换括号 + 映射标准门店名
            inflow_df['验证门店'] = inflow_df['验证门店'].map(to_full_width_brackets)
            inflow_df['验证门店'] = inflow_df['验证门店'].apply(map_to_standard_store)

            # -------- 预付 + 拼团 合计计算 -------- #
            valid_inflow = inflow_df[(inflow_df['订单状态'] == '已消费') & (inflow_df['订单来源'] != '直播')]
            prepaid_sum = valid_inflow.groupby('验证门店')['预付款金额'].sum().to_dict()

            valid_detail = detail_df[detail_df['订单类型'] == '拼团']
            detail_grouped = valid_detail.groupby('消费门店')[
                '结算价(总收入-美团点评技术服务费-商家营销费用-消费后退-其他调整)（元）'
            ].sum().to_dict()

            combined_store_total = {}
            # 取两个字典所有门店名的并集，避免漏门店
            all_stores = set(prepaid_sum.keys()) | set(detail_grouped.keys())
            for store_name in all_stores:
                combined_store_total[store_name] = prepaid_sum.get(store_name, 0) + detail_grouped.get(store_name, 0)

            # -------- 广告消耗 -------- #
            ad_cost_map = {}
            if not consult_df.empty:
                ad_grouped = consult_df.groupby('门店名称')['CPC消耗额'].sum().to_dict()
                ad_cost_map.update(ad_grouped)

            # -------- 实际佣金 -------- #
            commission_map = {}
            if not detail_df.empty:
                commission_grouped = detail_df.groupby('消费门店')['平台技术服务费（元）'].sum().abs().to_dict()
                commission_map.update(commission_grouped)

            # -------- 订单量与占比 -------- #
            order_count = {}
            order_ratio = {}
            if not detail_df.empty:
                valid_orders = detail_df[detail_df['收益类型'] != '已消费退']
                order_count = valid_orders.groupby('消费门店').size().to_dict()
                total_orders = sum(order_count.values())
                order_ratio = {
                    store: f"{(count / total_orders * 100):.2f}%" if total_orders > 0 else "0.00%"
                    for store, count in order_count.items()
                }

            # -------- 汇总输出 -------- #
            results = []
            summary_all = {
                '标准额度': 0,
                '实付核销金额（不含直播/刷单）': 0,
                '差额': 0,
                '实际佣金（不含直播/刷单）': 0,
                '广告消耗': 0,
                '总消耗': 0,
                '订单量': 0,
                '订单占比': '',
            }

            for store_name in standard_amount_config.keys():
                standard_config = standard_amount_config[store_name]
                standard_amount = standard_config['daily_amount'] * standard_config['days']

                expose = combined_store_total.get(store_name, 0)
                commission = commission_map.get(store_name, 0)
                ad_cost = ad_cost_map.get(store_name, 0)
                order_num = order_count.get(store_name, 0)
                order_percent = order_ratio.get(store_name, '0.00%')

                diff = expose - standard_amount
                total_cost = commission + ad_cost

                summary_all['标准额度'] += standard_amount
                summary_all['实付核销金额（不含直播/刷单）'] += expose
                summary_all['差额'] += diff
                summary_all['实际佣金（不含直播/刷单）'] += commission
                summary_all['广告消耗'] += ad_cost
                summary_all['总消耗'] += total_cost
                summary_all['订单量'] += order_num

                results.append({
                    '验证门店': store_name,
                    '佣金数据': {
                        '标准额度': to_int(standard_amount),
                        '实付核销金额（不含直播/刷单）': to_int(expose),
                        '差额': to_int(diff),
                        '实际佣金（不含直播/刷单）': to_int(commission),
                        '广告消耗': to_int(ad_cost),
                        '总消耗': to_int(total_cost),
                        '订单量': to_int(order_num),
                        '门店订单占比': order_percent
                    }
                })

            return DetailResponse({
                'data': results,
                '所有门店汇总': {k: to_int(v) for k, v in summary_all.items()}
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return DetailResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
