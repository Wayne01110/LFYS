from django.urls import path

from .views.lf_customer_activity import LFCustomerActivityView
from .views.lf_project_deal_rank import LFProjectDealRankView
from .views.lf_project_package_doctor import LFProjectPackageDoctorView
from .views.lf_sk import LFSKViewSet
from .views.lf_xcx_client_info import LFXcxClientInfoView
from .views.mt_commission import MTCommissionView
from .views.mt_inflow_outflow import MTInflowOutflowView
from .views.mt_store_invert import MTStoreInvertView

urlpatterns = [
    path('api/LFSKViewSet/', LFSKViewSet.as_view(), name='lf_sk'),                                                      # 水卡统计
    path('api/LFCustomerActivityView/', LFCustomerActivityView.as_view(), name='lf_customer_activity'),                 # 靓范最强咨询师排行
    path('api/LFProjectDealRankView/', LFProjectDealRankView.as_view(), name='lf_project_deal_rank'),                   # 咨询师项目销售排行
    path('api/LFXcxClientInfoView/', LFXcxClientInfoView.as_view(), name='lf_xcx_client_info'),                         # 小程序客户积分统计
    path('api/LFProjectPackageDoctorView/', LFProjectPackageDoctorView.as_view(), name='lf_project_package_doctor'),    # 项目&套餐排行AND医生划扣排行


    #美团
    path('api/MTInflowOutflowView/', MTInflowOutflowView.as_view(), name='mt_inflow_outflow'),              # 美团流入流出
    path('api/MTStoreInvertView/', MTStoreInvertView.as_view(), name='mt_store_invert'),                    # 美团门店转化报表
    path('api/MTCommissionView/', MTCommissionView.as_view(), name='mt_commission'),                        # 美团佣金表


]
