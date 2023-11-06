# from django.contrib.auth.models import User
from rest_framework import viewsets, generics
from rest_framework import permissions, status
from users.models import Party, StaffUser, Transaction, TransactionAssignment, Inspection, Property
from users.serializers import InspectionSerializer, TransactionAssignmentSerializer, WriteTransactionSerializer, UserSerializer, ReadTransactionSerializer, CustomerUserSerializer, StaffUserSerializer, PropertySerializer

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import MethodNotAllowed

from users.permissions import CanUpdateField, ReadOnlyOrPartialUpdatePermission

from rest_framework.response import Response
from rest_framework.decorators import action

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class CustomerUserViewSet(viewsets.ModelViewSet):
    queryset = Party.objects.all()
    serializer_class = CustomerUserSerializer
    # permission_classes = [IsParty]
    permission_classes = [permissions.IsAuthenticated]


class StaffUserViewSet(viewsets.ModelViewSet):
    queryset = StaffUser.objects.all()
    serializer_class = StaffUserSerializer
    # permission_classes = [IsStaffUser]
    permission_classes = [permissions.IsAuthenticated]


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated]


class TransactionViewSet(viewsets.ModelViewSet):
    """ 
    View for managing property transaction
    """
    queryset = Transaction.objects.all().order_by("-created_at")
    # serializer_class = TransactionWriteSerializer # I now use get_serializer_class
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return WriteTransactionSerializer
        return ReadTransactionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)  # NOQA
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # NOQA

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    # coordinator's view
    # TODO:Find a better way to handle this
    @action(detail=False, methods=['get', 'post'], url_path=r'verified')
    def verified(self, request):
        queryset = self.queryset.filter(is_verified=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# TODO: change this view to a generic view
class TransactionVerificationViewSet(viewsets.ModelViewSet):
    """ 
    View for ES to approve transactions 
    """
    queryset = Transaction.objects.all()
    serializer_class = WriteTransactionSerializer
    permission_classes = [ReadOnlyOrPartialUpdatePermission]

    def partial_update(self, request, *args, **kwargs):
        # Get the instance to be updated
        instance = self.get_object()

        # Update only the 'my_field_to_update' field to True
        instance.is_verified = True
        instance.save(update_fields=['is_verified'])

        return Response(self.get_serializer(instance).data)


class TransactionAssignmentViewSet(viewsets.ModelViewSet):
    queryset = TransactionAssignment.objects.all()
    serializer_class = TransactionAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    # http_method_names = ['get','post','retrieve','put','patch']


class InspectionViewSet(viewsets.ModelViewSet):
    queryset = Inspection.objects.all()
    serializer_class = InspectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        inspection = serializer.save()
        transaction = inspection.transaction_assigned.transaction
        if transaction:
            transaction.is_valuation_done = True
            transaction.save()


class UserAssignedTransactionsViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter TransactionAssignment instances by the 'assigned_to' field
        # Current authenticated user (StaffUser)
        return TransactionAssignment.objects.filter(assigned_to=self.request.user)

    # Override the destroy method to exclude DELETE
    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed(
            "DELETE method is not allowed for this resource.")
