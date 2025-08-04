from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
import os
import pandas as pd
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.views import APIView


class LFSKViewSet(APIView):
    permission_classes = []

    """
        add by Wayne 2025-06-07  水卡统计
    """

    def post(self, request):
        file = request.FILES.get('file')

        if not file:
            return Response({'error': '未找到上传的文件。'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            file_path = default_storage.save(f'temp/{file.name}', ContentFile(file.read()))
            file_full_path = os.path.join('media', file_path)
            df = pd.read_excel(file_full_path, header=1)

            selected_columns = [38, 62, 74, 83]
            df_filtered = df.iloc[:, selected_columns]
            df_filtered.columns = ['原订单开单人', '项目/商品/药品名称', '所属套餐', '本次结算业绩']

            # 移除存在缺失值的行
            df_filtered = df_filtered.dropna(subset=['所属套餐', '项目/商品/药品名称'])

            target_packages = [
                '水+光VIP嫩肤卡', '水+光VIP祛斑卡', '水嫩10连卡', '修丽可全系列3选10次卡', '修丽可全系列4选24次卡'
            ]
            target_products = [
                '丝缇珂-补水抗氧护理10次卡', '修丽可光电官配-5次卡', '修丽可光电官配-10次卡',
                '海菲秀四步曲-10次卡', '半岛舒敏专家全模式-3次卡', '半岛舒敏专家全模式-5次卡', '半岛舒敏专家全模式-10次卡'
            ]

            df_filtered = df_filtered[(df_filtered['本次结算业绩'] > 0) &
                                      (df_filtered['所属套餐'].isin(target_packages) |
                                       df_filtered['项目/商品/药品名称'].isin(target_products))]

            result = {}
            for name, group in df_filtered.groupby('原订单开单人'):
                result[name] = {
                    '项目/商品/药品名称统计': group['项目/商品/药品名称'].value_counts().to_dict(),
                    '所属套餐统计': group['所属套餐'].value_counts().to_dict(),
                }

            os.remove(file_full_path)  # 删除临时文件

            return Response({'data': result}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'数据处理错误: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
