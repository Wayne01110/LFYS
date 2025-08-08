import os
import pandas as pd
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.decorators import action
from dvadmin.utils.json_response import DetailResponse


class LFSKViewSet(APIView):
    permission_classes = []
    """
        add by Wayne 2025-03-19  咨询师水卡统计
    """
    # 出纳结算单上传
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return DetailResponse({'error': '未找到上传的文件。'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            file_path = default_storage.save(f'temp/{file.name}', ContentFile(file.read()))
            file_full_path = os.path.join('media', file_path)
            df = pd.read_excel(file_full_path, header=1)

            selected_columns = [4, 38, 62, 74, 76, 83]
            df_filtered = df.iloc[:, selected_columns]
            df_filtered.columns = ['会员号', '原订单开单人', '项目/商品/药品名称', '所属套餐', '数量', '本次结算业绩']

            # 所属套餐
            target_packages = [
                '水+光VIP嫩肤卡', '水+光VIP祛斑卡', '水嫩10连卡', '修丽可全系列3选10次卡', '修丽可全系列4选24次卡'
            ]
            # 项目/商品/药品名称
            target_products = [
                '丝缇珂-补水抗氧护理10次卡', '修丽可光电官配-5次卡', '修丽可光电官配-10次卡',
                '海菲秀四步曲-10次卡', '半岛舒敏专家全模式-3次卡', '半岛舒敏专家全模式-5次卡', '半岛舒敏专家全模式-10次卡'
            ]

            # 筛选符合套餐和项目/商品/药品名称的数据
            df_filtered_packages = df_filtered[(df_filtered['本次结算业绩'] > 0) &
                                               (df_filtered['所属套餐'].isin(target_packages))]
            df_filtered_products = df_filtered[(df_filtered['本次结算业绩'] > 0) &
                                               (df_filtered['项目/商品/药品名称'].isin(target_products))]
            result = {}
            # 处理套餐统计
            for name, group in df_filtered_packages.groupby('原订单开单人'):
                if name not in result:
                    result[name] = {
                        '项目/商品/药品名称统计': {},
                        '所属套餐统计': {}
                    }
                # 套餐统计
                package_counts = group['所属套餐'].value_counts().to_dict()
                # 处理“水嫩10连卡”统计
                water_card_groups = group[group['所属套餐'] == '水嫩10连卡'].groupby('会员号')
                water_card_count = 0
                for member_id, member_group in water_card_groups:
                    if member_group['数量'].sum() == 10:
                        water_card_count += 1
                if '水嫩10连卡' in package_counts:
                    package_counts['水嫩10连卡'] = water_card_count

                result[name]['所属套餐统计'] = package_counts

            # 处理项目/商品/药品名称统计
            for name, group in df_filtered_products.groupby('原订单开单人'):
                if name not in result:
                    result[name] = {
                        '项目/商品/药品名称统计': {},
                        '所属套餐统计': {}
                    }
                result[name]['项目/商品/药品名称统计'] = group['项目/商品/药品名称'].value_counts().to_dict()

            os.remove(file_full_path)  # 删除临时文件

            return DetailResponse({'data': result}, status=status.HTTP_200_OK)
        except Exception as e:
            return DetailResponse({'error': f'数据处理错误: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

