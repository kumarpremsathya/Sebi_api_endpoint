from django.urls import path
from  .views import *

urlpatterns = [
    
    path('<str:type_of_order>/getSebiOrderByYear/', GetOrderYearView.as_view(), name='getSebiOrderByYear'),  
    path('<str:type_of_order>/download_all_pdfs/', DownloadAllPDFsView.as_view(), name='download_all_pdfs'),
   
    
    path('<str:type_of_order>/getSebiOrderByDate/', GetOrderDateView.as_view(), name='getSebiOrderByDate'),  
    path('<str:type_of_order>/download_pdfs/', DownloadPDFsView.as_view(), name='download_pdfs'),
    
    path('<path:invalid_path>', Custom404View.as_view(), name='invalid_path'),
    # path('<str:whether>/getSebiOrderByDate/<int:year>/<int:month>/', GetOrderdateView.as_view(), name='getSebiOrderByDate'),
    # path('<str:whether>/getSebiOrderByDate/<int:year>/<int:month>/<int:day>/',GetOrderdateView.as_view(), name='getSebiOrderByDate'),
 
    
   
 
    # path('getOrdermonthView/',GetOrdermonthView.as_view(), name='GetOrdermonthView'),
    # path('getOrdertotalview/',GetOrdertotalview.as_view(), name='GetOrdertotalview')
]




