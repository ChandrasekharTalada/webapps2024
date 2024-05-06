from payapp import views
from django.urls import path


urlpatterns = [
    path('home/', views.HomeView.as_view(), name='home'),
    path('request/',views.RequestDetailView.as_view(),name="transfer_request"),
    path('transaction/',views.TransactionDetailView.as_view(),name="transaction"),
    path("transaction/all/",views.AllTransactionView.as_view(),name="transaction_all"),
    path('amount/transfer/',views.SendPayment.as_view(),name="amount_send"),
    path('amount/request/',views.RequestPayment.as_view(),name="amount_request"),
    path('amount/request/approve/',views.ApprovePaymentRequest.as_view(),name="amount_request_approve"),
    path('amount/request/reject/',views.RejectPaymentRequest.as_view(),name="amount_request_reject"),
    path('notification/',views.NotificationView.as_view(),name="notification"),
    path('get_unseen_notification/',views.NotificationUnseen.as_view(),name="get_unseen_notification"),
    path('mark_as_seen/<int:id>/',views.NotificationMarkSeen.as_view(),name="mark_as_seen"),
]

