import os
import pandas as pd
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework import status
from dvadmin.utils.json_response import DetailResponse


class MTStoreInvertView(APIView):
    permission_classes = []
    """
        add by Wayne 2025-08-02  美团门店转化报表
    """

    def post(self, request):
        files = request.FILES.getlist('files')
        if not files:
            return DetailResponse({'error': '请上传文件'}, status=status.HTTP_400_BAD_REQUEST)

        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')

        try:
            # 识别文件
            inflow_file = detail_file = consult_file = None
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

            # 读取来源业绩分析表，处理多级表头
            inflow_path = default_storage.save(f'temp/{inflow_file.name}', ContentFile(inflow_file.read()))
            inflow_df_raw = pd.read_excel(os.path.join('media', inflow_path), sheet_name='来源成交统计', header=[0, 1])
            inflow_df_raw.columns = [
                col[1] if col[0] == '新客' else (col[0] if 'Unnamed' in col[1] or pd.isna(col[1]) else f"{col[0]}_{col[1]}")
                for col in inflow_df_raw.columns
            ]
            inflow_df = inflow_df_raw.fillna(method='ffill')

            # 读取门店明细，补齐字段
            detail_df = None
            if detail_file:
                detail_path = default_storage.save(f'temp/{detail_file.name}', ContentFile(detail_file.read()))
                detail_df = pd.read_excel(os.path.join('media', detail_path)).fillna(0)
                detail_df = detail_df.rename(columns=lambda x: str(x).strip())
                for col in ['CPC消耗额', '广告曝光次数', '广告点击量', '广告访问次数']:
                    if col not in detail_df.columns:
                        detail_df[col] = 0

            # 读取线上咨询表，过滤日期
            consult_df = None
            private_msg_counts = {}
            if consult_file:
                consult_path = default_storage.save(f'temp/{consult_file.name}', ContentFile(consult_file.read()))
                consult_df = pd.read_excel(os.path.join('media', consult_path), sheet_name='美团咨询表', header=0)
                if '日期' not in consult_df.columns:
                    return DetailResponse({'error': '美团咨询表中缺少“日期”列'}, status=status.HTTP_400_BAD_REQUEST)
                consult_df['日期'] = pd.to_datetime(consult_df['日期'], errors='coerce')
                if start_date:
                    consult_df = consult_df[consult_df['日期'] >= pd.to_datetime(start_date)]
                if end_date:
                    consult_df = consult_df[consult_df['日期'] <= pd.to_datetime(end_date)]

            # 映射关系
            name_mapping = {
                '靓范医生医美连锁（松北万象汇院区）': '哈尔滨松北美团点评',
                '靓范医生医美连锁（万象城院区）': '长春万象美团点评',
                '靓范医生医美连锁（远大购物中心院区）': '长春远大美团点评',
                '靓范医生医美连锁（净月院区）': '长春净月美团点评',
                '靓范医生医美连锁（呼市万象城院区）': '呼和浩特万象点评',
                '靓范医生医美连锁（欧亚新生活院区）': '长春欧亚美团点评',
                '靓范医生医美连锁（郑东万象城院区）': '郑州万象美团点评',
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

            def map_consult_store(x):
                return consult_store_map.get(str(x).strip(), None)

            if consult_df is not None:
                consult_df['点评来源'] = consult_df['门店'].apply(map_consult_store)
                consult_df = consult_df[consult_df['点评来源'].notna()]
                private_msg_counts = consult_df.groupby('点评来源').size().to_dict()

            def to_percent(value):
                try:
                    return f"{float(value) * 100:.2f}%"
                except:
                    return "0.00%"

            def to_int(value):
                try:
                    return int(round(float(value)))
                except:
                    return 0

            results = []
            summary_all = {
                '流出-新客': {'初诊人数': 0, '初诊成交': 0, '初复诊成交': 0, '新客业绩': 0.0},
                '推广数据': {'门店CPC消耗': 0.0, '广告曝光次数': 0, '广告点击量': 0, '广告访问次数': 0, '私信': 0}
            }

            for name, source in name_mapping.items():
                # 筛选流出-新客数据（来源一级=美团点评，来源二级=source，开单人为门店小计）
                out_rows = inflow_df[
                    (inflow_df['来源一级'] == '美团点评') &
                    (inflow_df['来源二级'] == source) &
                    (inflow_df['开单人'] == '门店小计')
                    ]

                out_details_sum = {'初诊人数': 0, '初诊成交': 0, '初复诊成交': 0, '新客业绩': 0.0}
                for _, row in out_rows.iterrows():
                    out_details_sum['初诊人数'] += row['初诊人数']
                    out_details_sum['初诊成交'] += row['初诊成交']
                    out_details_sum['初复诊成交'] += row['初复诊成交']
                    out_details_sum['新客业绩'] += row['新客业绩']

                # 门店明细中的广告数据
                store_detail = detail_df[detail_df.iloc[:, 0] == name] if detail_df is not None else pd.DataFrame()
                cpc = store_detail['CPC消耗额'].sum() if not store_detail.empty else 0.0
                expose = store_detail['广告曝光次数'].sum() if not store_detail.empty else 0
                click = store_detail['广告点击量'].sum() if not store_detail.empty else 0
                visit = store_detail['广告访问次数'].sum() if not store_detail.empty else 0

                # 线上咨询私信数
                msg_count = private_msg_counts.get(source, 0)

                # 计算率和投产比
                click_rate = f"{(click / expose * 100):.2f}%" if expose else "0.00%"
                diagnosis_rate = f"{(out_details_sum['初诊人数'] / msg_count * 100):.2f}%" if msg_count else "0.00%"
                revisit_rate = f"{(out_details_sum['初复诊成交'] / out_details_sum['初诊人数'] * 100):.2f}%" if out_details_sum['初诊人数'] else "0.00%"
                roi = round(out_details_sum['新客业绩'] / cpc, 2) if cpc else 0.0

                out_summary_formatted = {
                    '初诊人数': out_details_sum['初诊人数'],
                    '初诊成交': out_details_sum['初诊成交'],
                    '初复诊成交': out_details_sum['初复诊成交'],
                    '新客业绩': to_int(out_details_sum['新客业绩']),
                    '初诊到诊率': diagnosis_rate,
                    '初诊成交率': to_percent(out_details_sum['初诊成交'] / out_details_sum['初诊人数']) if out_details_sum['初诊人数'] else "0.00%",
                    '初复诊成交率': revisit_rate,
                    '新客客单价': to_int(out_details_sum['新客业绩'] / out_details_sum['初诊成交']) if out_details_sum['初诊成交'] else 0,
                }

                # 汇总所有门店数据
                summary_all['流出-新客']['初诊人数'] += out_details_sum['初诊人数']
                summary_all['流出-新客']['初诊成交'] += out_details_sum['初诊成交']
                summary_all['流出-新客']['初复诊成交'] += out_details_sum['初复诊成交']
                summary_all['流出-新客']['新客业绩'] += out_details_sum['新客业绩']

                summary_all['推广数据']['门店CPC消耗'] += cpc
                summary_all['推广数据']['广告曝光次数'] += expose
                summary_all['推广数据']['广告点击量'] += click
                summary_all['推广数据']['广告访问次数'] += visit
                summary_all['推广数据']['私信'] += msg_count

                results.append({
                    '点评来源': source,
                    '推广数据': {
                        '门店CPC消耗': round(cpc, 2),
                        '广告曝光次数': int(expose),
                        '广告点击量': int(click),
                        '广告访问次数': int(visit),
                        '点击率': click_rate,
                        '私信': msg_count,
                    },
                    '流出-新客': out_summary_formatted,
                    '投产比': {
                        '新客投产比': roi
                    }
                })

            return DetailResponse({
                'data': results,
                '所有门店汇总': summary_all
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return DetailResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
