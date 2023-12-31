from django.urls import include, path
from rest_framework import routers
from users import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
# router.register(r'groups', views.GroupViewSet)

router.register(r'party', views.CustomerUserViewSet, basename='party')
router.register(r'staffs', views.StaffUserViewSet, basename='staff')
router.register(r'transactions', views.TransactionViewSet,
                basename='transactions')
router.register(r'task_assignments',
                views.TransactionAssignmentViewSet, basename='task_assignments')
router.register(r'user_assigned_transactions',
                views.UserAssignedTransactionsViewSet, basename='user-assigned-transactions')
router.register(r'transaction_verification',
                views.TransactionVerificationViewSet, basename='transaction-verification')
router.register(r'inspections', views.InspectionViewSet,
                basename='inspections')
router.register(r'properties', views.PropertyViewSet,
                basename='property')


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browserable API.
urlpatterns = [
    path('api/', include(router.urls)),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
    path('change-password/', views.ChangePasswordView.as_view(),
         name='change-password'),
]
