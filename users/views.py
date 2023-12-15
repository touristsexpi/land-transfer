# from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, generics, status, permissions
from users.models import Party, StaffUser, Transaction, TransactionAssignment, Inspection, Property, InspectionImage
from users.serializers import InspectionSerializer, TransactionAssignmentSerializer, VerifyTransactionSerializer, WriteTransactionSerializer, UserSerializer, ReadTransactionSerializer, PartySerializer, StaffUserSerializer, PropertySerializer, ChangePasswordSerializer

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from rest_framework.exceptions import MethodNotAllowed

from users.permissions import CanUpdateField, ReadOnlyOrPartialUpdatePermission, UserPermission

from rest_framework.response import Response
from rest_framework.decorators import action

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UserPermission,]


class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not request.user.check_password(serializer.data.get("old_password")):
                return Response({"detail": "Invalid old password."}, status=status.HTTP_400_BAD_REQUEST)

            # Set new password
            request.user.set_password(serializer.data.get("new_password"))
            request.user.save()
            return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class ChangePasswordView(generics.UpdateAPIView):
#     queryset = User.objects.all()
#     serializer_class = ChangePasswordSerializer
#     # permission_classes = []

class CustomerUserViewSet(viewsets.ModelViewSet):
    queryset = Party.objects.all()
    serializer_class = PartySerializer
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

    # def perform_create(self, serializer):
    #     serializer.save(created_by=self.request.user)


class TransactionViewSet(viewsets.ModelViewSet):
    """ 
    View for managing property transaction
    """
    queryset = Transaction.objects.all()
    # serializer_class = TransactionWriteSerializer # I now use get_serializer_class
    # parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'put', 'delete']

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
    @action(detail=False, methods=['get', ], url_path=r'un-verified')
    def un_verified(self, request):
        unverified = self.queryset.filter(is_verified=False)
        serializer = VerifyTransactionSerializer(unverified, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path=r'toggle-verified')
    def toggle_verified_status(self, request, pk=None):
        transaction = self.get_object()

        if 'is_verified' in request.data:
            transaction.is_verified = request.data['is_verified']
            transaction.save()
            serializer = VerifyTransactionSerializer(transaction)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid data for partial update.'}, status=status.HTTP_400_BAD_REQUEST)


class TransactionVerificationViewSet(viewsets.ModelViewSet):
    """ 
    View for ES to approve transactions 
    """
    queryset = Transaction.objects.all().filter(is_verified=False)
    serializer_class = VerifyTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    # permission_classes = [ReadOnlyOrPartialUpdatePermission]
    http_method_names = ['get', 'patch']

    def perform_update(self, serializer):
        serializer.save()

    # def partial_update(self, request, *args, **kwargs):
    #     # Get the instance to be updated
    #     instance = self.get_object()

    #     # Update only the 'my_field_to_update' field to True
    #     instance.is_verified = True
    #     instance.save(update_fields=['is_verified'])

    #     return Response(self.get_serializer(instance).data)


class TransactionAssignmentViewSet(viewsets.ModelViewSet):
    queryset = TransactionAssignment.objects.all().filter(transaction__is_verified=True)
    serializer_class = TransactionAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'retrieve',
                         'put', 'patch']  # is PATCH necessary?

    # def perform_create(self, serializer):
    #     serializer.save(creator=self.request.user)


class InspectionViewSet(viewsets.ModelViewSet):
    queryset = Inspection.objects.all()
    serializer_class = InspectionSerializer
    # parser_classes = (MultiPartParser, FormParser, FileUploadParser)
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        inspection = serializer.save()
        transaction = inspection.transaction_assigned.transaction
        if transaction:
            transaction.is_valuation_done = True
            transaction.save()

    # def create(self, request, *args, **kwargs):
    #     item_serializer = self.get_serializer(data=request.data)
    #     item_serializer.is_valid(raise_exception=True)
    #     self.perform_create(item_serializer)

    #     # Handle image uploads
    #     images_data = request.FILES.getlist('image')
    #     for image_data in images_data:
    #         InspectionImage.objects.create(
    #             item=item_serializer.instance, image=image_data)

    #     # Handle PDF upload
    #     pdf_file = request.FILES.get('file_path')
    #     if pdf_file:
    #         inspection_instance = item_serializer.instance
    #         inspection_instance.file_path = pdf_file
    #         inspection_instance.save()

    #     headers = self.get_success_headers(item_serializer.data)
    #     return Response(item_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


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
