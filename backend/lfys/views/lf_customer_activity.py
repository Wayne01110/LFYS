import os
import pandas as pd
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework import status

from dvadmin.utils.json_response import DetailResponse


class LFCustomerActivityView(APIView):
    permission_classes = []

    """
        add by Wayne 2025-04-07  靓范最强咨询师排行
    """

    def post(self, request):

        files = request.FILES.getlist('files')  # 获取多个文件
        if not files or len(files) < 2:
            return DetailResponse({'error': '请同时上传咨询维度.xlsx 和 顾客维度.xlsx'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # 初复诊业绩
            row_37 = None
            # 初复诊客单
            row_33 = None
            # 初复诊成交人数
            row_31 = None
            # 初复诊到院人数
            row_29 = None
            # 初复诊成交率
            row_32 = None
            # 老客业绩
            row_51 = None
            # 老客客单价
            row_47 = None
            # 老客到院人数
            row_42 = None
            # 老客成交人数
            row_45 = None
            # 老客成交率
            row_46 = None
            # 老带新业绩
            row_63 = None
            # 老带新客单价
            row_59 = None
            # 老带新成交人数
            row_57 = None
            # 老带新到院人数
            row_55 = None
            # 老带新成交率
            row_58 = None
            df_customer = None
            xls = ""
            file_full_path = ""
            for file in files:
                # 保存上传的文件
                file_path = default_storage.save(f'temp/{file.name}', ContentFile(file.read()))
                file_full_path = os.path.join('media', file_path)
                xls = pd.ExcelFile(file_full_path)
                # 读取对应的 Excel 表
                if '咨询维度' in file.name:  # 处理咨询维度.xlsx
                    df_consulting = xls.parse(sheet_name='咨询业绩')
                    selected_columns = [4, 5, 6, 7, 10, 11, 14, 15, 16, 19, 20, 21, 23, 24, 27, 28, 31, 32]
                    df_consulting = df_consulting.iloc[:, selected_columns]
                    # 老客成交人数
                    row_45 = df_consulting.iloc[45]
                    # 老客到院人数
                    row_42 = df_consulting.iloc[42]
                    # 老客业绩
                    row_51 = df_consulting.iloc[51]
                    # 老客客单价
                    row_47 = df_consulting.iloc[47]
                    # 老客成交率
                    row_46 = df_consulting.iloc[46]
                    # 初复诊成交人数
                    row_31 = df_consulting.iloc[31]
                    # 初复诊到院人数
                    row_29 = df_consulting.iloc[29]
                    # 初复诊业绩
                    row_37 = df_consulting.iloc[37]
                    # 初复诊客单
                    row_33 = df_consulting.iloc[33]
                    # 初复诊成交率
                    row_32 = df_consulting.iloc[32]
                    # 老带新业绩
                    row_63 = df_consulting.iloc[63]
                    # 老带新成交人数
                    row_57 = df_consulting.iloc[57]
                    # 老带新到院人数
                    row_55 = df_consulting.iloc[55]
                    # 老带新客单价
                    row_59 = df_consulting.iloc[59]
                    # 老带新成交率
                    row_58 = df_consulting.iloc[58]
                if '顾客维度' in file.name:  # 处理顾客维度.xlsx
                    df_customer = xls.parse(sheet_name='简化版')
            # 检查是否成功获取数据
            # if (row_45 or row_51 or row_57 or row_37 or row_32 or row_47 or row_46) is None:
            #     return DetailResponse({'error': '未找到咨询维度数据，请检查上传的 Excel 文件'}, status=status.HTTP_400_BAD_REQUEST)
            if df_customer is None:
                return DetailResponse({'error': '未找到顾客维度数据，请检查上传的 Excel 文件'}, status=status.HTTP_400_BAD_REQUEST)
            # 【Step 1】读取顾客维度数据
            customer_mapping = df_customer.iloc[:, [2, 3]]
            customer_mapping.columns = ['咨询师', '顾客总数不含E类']
            # 只保留 consultants 列表中的咨询师
            consultants = ['李昭蓉', '姜雪薇', '王娇', '范红霄', '贾烁旸', '姜雪',
                           '徐佳萌', '齐霖', '王爽', '朴丽颖', '张晴', '李佳怡1', '李壹然', '崔雨竹',
                           '石金宇', '李桥', '任莹莹', '常效闻']
            customer_mapping = customer_mapping[customer_mapping['咨询师'].isin(consultants)]
            # 将 "顾客总数不含E类" 设为数值类型，非数值用 0 填充
            customer_mapping['顾客总数不含E类'] = pd.to_numeric(customer_mapping['顾客总数不含E类'], errors='coerce').fillna(0).astype(int)
            # 【Step 2】构建结果 DataFrame
            result_df = pd.DataFrame({
                '咨询师': consultants,
                '老客成交人数': row_45.astype(int),
                '老客到院人数': row_42.astype(int),
                '老客业绩': row_51.astype(int),
                '老客客单价': row_47.astype(int),
                '老客成交率': row_46,
                '初复诊成交人数': row_31.astype(int),
                '初复诊到院人数': row_29.astype(int),
                '初复诊业绩': row_37.astype(int),
                '初复诊客单价': row_33.astype(int),
                '初复诊成交率': row_32,
                '老带新成交人数': row_57.astype(int),
                '老带新到院人数': row_55.astype(int),
                '老带新业绩': row_63.astype(int),
                '老带新客单价': row_59.astype(int),
                '老带新成交率': row_58,
            })
            # 将成交率转为百分比并保留两位小数
            result_df['老客成交率'] = result_df['老客成交率'].apply(lambda x: f'{x * 100:.2f}%' if pd.notna(x) else '0.00%')
            result_df['初复诊成交率'] = result_df['初复诊成交率'].apply(lambda x: f'{x * 100:.2f}%' if pd.notna(x) else '0.00%')
            result_df['老带新成交率'] = result_df['老带新成交率'].apply(lambda x: f'{x * 100:.2f}%' if pd.notna(x) else '0.00%')
            # 【Step 3】合并顾客总数不含E类
            result_df = result_df.merge(customer_mapping, on='咨询师', how='left')
            # 【Step 4】填充缺失值（如果某个咨询师没有匹配到数据，则顾客总数设为 0）
            result_df['顾客总数不含E类'] = result_df['顾客总数不含E类'].fillna(0).astype(int)
            # 【Step 5】计算顾客活跃度（百分比格式，保留两位小数）
            result_df['顾客活跃度'] = result_df.apply(
                lambda row: f"{round((row['老客到院人数'] / row['顾客总数不含E类']) * 100, 2)}%" if row['顾客总数不含E类'] > 0 else "0.00%",
                axis=1
            )
            # 转换顾客活跃度为 float 进行排序
            result_df['顾客活跃度数值'] = result_df['顾客活跃度'].str.rstrip('%').astype(float)
            result_df = result_df.sort_values(by='顾客活跃度数值', ascending=False)
            # 删除临时数值列
            result_df = result_df.drop(columns=['顾客活跃度数值'])
            # 转换为字典格式
            result = result_df.to_dict(orient='records')
            xls.close()
            # 删除临时文件
            os.remove(file_full_path)
            return DetailResponse({'data': result}, status=status.HTTP_200_OK)
        except Exception as e:
            return DetailResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
