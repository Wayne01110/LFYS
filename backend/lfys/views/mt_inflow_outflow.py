import os
import pandas as pd
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework import status

from dvadmin.utils.json_response import DetailResponse


class MTInflowOutflowView(APIView):
    permission_classes = []
    """
        add by Wayne 2025-08-02  美团流入流出
    """

    def post(self, request):
        files = request.FILES.getlist('files')
        if not files:
            return DetailResponse({'error': '请上传文件'}, status=status.HTTP_400_BAD_REQUEST)

        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')

        try:
            inflow_file = None
            detail_file = None
            consult_file = None

            for file in files:
                if '来源业绩分析（不含今日）' in file.name:
                    inflow_file = file
                elif '门店明细' in file.name:
                    detail_file = file
                elif '2025线上咨询表' in file.name:
                    consult_file = file

            if not inflow_file:
                return DetailResponse({'error': '未找到包含“来源业绩分析（不含今日）”的文件'},
                                      status=status.HTTP_400_BAD_REQUEST)

            # 读取来源业绩分析
            inflow_path = default_storage.save(f'temp/{inflow_file.name}', ContentFile(inflow_file.read()))
            inflow_full_path = os.path.join('media', inflow_path)
            inflow_df_raw = pd.read_excel(inflow_full_path, sheet_name='来源成交统计', header=[0, 1])

            new_columns = []
            for col in inflow_df_raw.columns:
                if col[0] == '新客':
                    new_columns.append(col[1])
                elif 'Unnamed' in col[1] or pd.isna(col[1]):
                    new_columns.append(col[0])
                else:
                    new_columns.append(f"{col[0]}_{col[1]}")

            inflow_df_raw.columns = new_columns
            inflow_df = inflow_df_raw.copy()
            # 对指标字段空值直接填0，防止计算时出错
            metrics_cols = ['初诊人数', '初诊成交', '初复诊成交', '新客业绩', '初诊成交率', '新客成交率', '客单价']
            for col in metrics_cols:
                if col in inflow_df.columns:
                    inflow_df[col] = inflow_df[col].fillna(0)


        # 读取门店明细
            detail_df = None
            if detail_file:
                detail_path = default_storage.save(f'temp/{detail_file.name}', ContentFile(detail_file.read()))
                detail_full_path = os.path.join('media', detail_path)
                detail_df = pd.read_excel(detail_full_path)

            # 读取2025线上咨询表
            consult_df = None
            private_msg_counts = {}
            if consult_file:
                consult_path = default_storage.save(f'temp/{consult_file.name}', ContentFile(consult_file.read()))
                consult_full_path = os.path.join('media', consult_path)

                consult_df = pd.read_excel(consult_full_path, sheet_name='美团咨询表', header=0)
                if '日期' not in consult_df.columns:
                    return DetailResponse({'error': '美团咨询表中缺少“日期”列，请检查表格格式'}, status=status.HTTP_400_BAD_REQUEST)

                consult_df['日期'] = pd.to_datetime(consult_df['日期'], errors='coerce')

                # 日期过滤
                if start_date:
                    consult_df = consult_df[consult_df['日期'] >= pd.to_datetime(start_date)]
                if end_date:
                    consult_df = consult_df[consult_df['日期'] <= pd.to_datetime(end_date)]

            name_mapping = {
                '靓范医生医美连锁（松北万象汇院区）': '哈尔滨松北美团点评',
                '靓范医生医美连锁（万象城院区）': '长春万象美团点评',
                '靓范医生医美连锁（远大购物中心院区）': '长春远大美团点评',
                '靓范医生医美连锁（净月院区）': '长春净月美团点评',
                '靓范医生医美连锁（呼市万象城院区）': '呼和浩特万象点评',
                '靓范医生医美连锁（欧亚新生活院区）': '长春欧亚美团点评',
                '靓范医生医美连锁（郑东万象城院区）': '郑州万象美团点评',
            }

            reverse_name_mapping = {
                '呼和浩特万象点评': '呼和浩特-万象店',
                '哈尔滨松北美团点评': '哈尔滨-万象汇店',
                '郑州万象美团点评': '郑州-万象店',
                '长春万象美团点评': '长春-万象店',
                '长春净月美团点评': '长春-东樾店',
                '长春远大美团点评': '长春-远大店',
                '长春欧亚美团点评': '长春-欧亚店',
            }

            consult_store_map = {
                '呼市万象': '呼和浩特万象点评',
                '净月': '长春净月美团点评',
                '欧亚': '长春欧亚美团点评',
                '松北万象汇': '哈尔滨松北美团点评',
                '万象': '长春万象美团点评',
                '远大': '长春远大美团点评',
                '郑东万象城': '郑州万象美团点评',
            }

            def map_consult_store(store_name):
                store_name_clean = str(store_name).strip()
                # 严格匹配字典键
                return consult_store_map.get(store_name_clean, None)

            if consult_df is not None:
                consult_df['点评来源'] = consult_df['门店'].apply(map_consult_store)
                consult_df = consult_df[consult_df['点评来源'].notna()]

                # 按点评来源统计私信数量（咨询条数）
                private_msg_counts = consult_df.groupby('点评来源').size().to_dict()

            flow_detail_df = inflow_df[
                (inflow_df['来源一级'] == '美团点评') &
                (inflow_df['开单人'] == '门店小计')
                ]

            flow_grouped = flow_detail_df.groupby(['来源二级', '门店']).agg({
                '初诊人数': 'sum',
                '初诊成交': 'sum',
                '初复诊成交': 'sum',
                '新客业绩': 'sum',
                '初诊成交率': 'mean',
                '新客成交率': 'mean',
                '客单价': 'mean',
            }).reset_index()

            results = []
            summary_all = {
                '流出': {'初诊人数': 0, '初诊成交': 0, '初复诊成交': 0, '新客业绩': 0.0},
                '流入': {'初诊人数': 0, '初诊成交': 0, '初复诊成交': 0, '新客业绩': 0.0},
            }

            def to_percent_str(value):
                try:
                    return f"{float(value) * 100:.2f}%"
                except:
                    return "0.00%"

            def to_int_round(value):
                try:
                    return int(round(float(value)))
                except:
                    return 0

            for name, source in name_mapping.items():
                out_rows = inflow_df[
                    (inflow_df['来源一级'] == '美团点评') &
                    (inflow_df['来源二级'] == source) &
                    (inflow_df['开单人'] == '门店小计')
                    ]

                out_details = []
                out_summary = {'初诊人数': 0, '初诊成交': 0, '初复诊成交': 0, '新客业绩': 0.0}
                for _, row in out_rows.iterrows():
                    out_details.append({
                        '点评来源': source,
                        '流出门店': row['门店'],
                        '方向': '流出',
                        '初诊人数': row['初诊人数'],
                        '初诊成交': row['初诊成交'],
                        '初复诊成交': row['初复诊成交'],
                        '初诊成交率': row['初诊成交率'],
                        '新客成交率': row['新客成交率'],
                        '新客业绩': row['新客业绩'],
                        '客单价': row['客单价'],
                    })
                    out_summary['初诊人数'] += row['初诊人数']
                    out_summary['初诊成交'] += row['初诊成交']
                    out_summary['初复诊成交'] += row['初复诊成交']
                    out_summary['新客业绩'] += row['新客业绩']

                cpc_value = 0.0
                if detail_df is not None:
                    cpc_value = detail_df[detail_df.iloc[:, 0] == name]['CPC消耗额'].sum()

                in_store_name = reverse_name_mapping.get(source)
                in_details = []
                in_summary = {'初诊人数': 0, '初诊成交': 0, '初复诊成交': 0, '新客业绩': 0.0}

                if in_store_name:
                    inflow_rows = flow_grouped[flow_grouped['门店'] == in_store_name]
                    for _, row in inflow_rows.iterrows():
                        in_details.append({
                            '点评来源': row['来源二级'],
                            '流入门店': row['门店'],
                            '方向': '流入',
                            '初诊人数': row['初诊人数'],
                            '初诊成交': row['初诊成交'],
                            '初复诊成交': row['初复诊成交'],
                            '初诊成交率': row['初诊成交率'],
                            '新客成交率': row['新客成交率'],
                            '新客业绩': row['新客业绩'],
                            '客单价': row['客单价'],
                        })
                        in_summary['初诊人数'] += row['初诊人数']
                        in_summary['初诊成交'] += row['初诊成交']
                        in_summary['初复诊成交'] += row['初复诊成交']
                        in_summary['新客业绩'] += row['新客业绩']

                private_msg_count = private_msg_counts.get(source, 0)

                summary_all['流出']['初诊人数'] += out_summary['初诊人数']
                summary_all['流出']['初诊成交'] += out_summary['初诊成交']
                summary_all['流出']['初复诊成交'] += out_summary['初复诊成交']
                summary_all['流出']['新客业绩'] += out_summary['新客业绩']

                summary_all['流入']['初诊人数'] += in_summary['初诊人数']
                summary_all['流入']['初诊成交'] += in_summary['初诊成交']
                summary_all['流入']['初复诊成交'] += in_summary['初复诊成交']
                summary_all['流入']['新客业绩'] += in_summary['新客业绩']

                if private_msg_count > 0:
                    diagnosis_rate = (out_summary['初诊人数'] / private_msg_count) * 100
                    diagnosis_rate_str = f"{diagnosis_rate:.2f}%"
                else:
                    diagnosis_rate_str = "0.00%"

                out_summary_formatted = out_summary.copy()
                out_summary_formatted['新客业绩'] = to_int_round(out_summary['新客业绩'])
                out_summary_formatted['初诊成交率'] = (
                    to_percent_str(out_summary['初诊成交'] / out_summary['初诊人数'])
                    if out_summary['初诊人数'] else "0.00%"
                )
                out_summary_formatted['新客成交率'] = (
                    to_percent_str(out_summary['初复诊成交'] / out_summary['初诊人数'])
                    if out_summary['初诊人数'] else "0.00%"
                )
                out_summary_formatted['客单价'] = (
                    to_int_round(out_summary['新客业绩'] / out_summary['初复诊成交'])
                    if out_summary['初复诊成交'] else 0
                )

                in_summary_formatted = in_summary.copy()
                if in_store_name:
                    filtered_in_rows = flow_grouped[flow_grouped['门店'] == in_store_name]

                    in_summary_formatted['新客业绩'] = to_int_round(in_summary['新客业绩'])
                    in_summary_formatted['初诊成交率'] = (
                        to_percent_str(filtered_in_rows['初诊成交'].sum() / filtered_in_rows['初诊人数'].sum())
                        if filtered_in_rows['初诊人数'].sum() else "0.00%"
                    )
                    in_summary_formatted['新客成交率'] = (
                        to_percent_str(filtered_in_rows['初复诊成交'].sum() / filtered_in_rows['初诊人数'].sum())
                        if filtered_in_rows['初诊人数'].sum() else "0.00%"
                    )
                    in_summary_formatted['客单价'] = (
                        to_int_round(filtered_in_rows['新客业绩'].sum() / filtered_in_rows['初复诊成交'].sum())
                        if filtered_in_rows['初复诊成交'].sum() else 0
                    )
                else:
                    in_summary_formatted['初诊成交率'] = "0.00%"
                    in_summary_formatted['新客成交率'] = "0.00%"
                    in_summary_formatted['新客业绩'] = 0
                    in_summary_formatted['客单价'] = 0

                results.append({
                    '点评来源': source,
                    '门店CPC消耗': round(cpc_value, 2),
                    '私信': private_msg_count,
                    '初诊到诊率': diagnosis_rate_str,
                    '流出明细': out_details,
                    '流出总计': out_summary_formatted,
                    '流入明细': in_details,
                    '流入总计': in_summary_formatted,
                })

            return DetailResponse({
                'data': results,
                '所有门店汇总': summary_all
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return DetailResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
