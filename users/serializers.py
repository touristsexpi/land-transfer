from django.contrib.auth.models import User, Group
from rest_framework import serializers

from users.models import Party, Property, StaffUser, Transaction, TransactionAssignment, Inspection


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class CustomerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        # fields = '__all__'
        fields = ('id', 'first_name', 'middle_name', 'last_name', 'identification', 'email', 'phone_number', 'dob', 'gender',
                  'address', 'city', 'post_code', 'natural_person', 'citizenship', )


class StaffUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffUser
        fields = '__all__'


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    # property = serializers.SlugRelatedField(
    #     many=False,
    #     read_only=True,
    #     slug_field="zupin")

    property = serializers.ReadOnlyField(read_only=True)
    transferor = CustomerUserSerializer(many=True, read_only=True)
    transferee = CustomerUserSerializer(many=True, read_only=True)
    # transferee = serializers.SlugRelatedField(
    # many=True,
    # read_only=True,
    # slug_field="identification")

    creator = serializers.ReadOnlyField(source='created_by.email')
    creator_id = serializers.ReadOnlyField(
        source='created_by.get_full_name')  # it was phone_number previously

    class Meta:
        model = Transaction
        # fields = '__all__'
        fields = ('id', 'type', 'form_number', 'registration_number', 'property', 'file_path',
                  'purchase_price', 'received_from', 'transferee', 'transferor', 'notes', 'creator', 'creator_id',)


class TransactionAssignmentSerializer(serializers.ModelSerializer):

    assigned_person = serializers.ReadOnlyField(
        source='assigned_to.get_full_name',)
    assigned_department = serializers.ReadOnlyField(
        source='assigned_to.department')
    assigned_by = serializers.ReadOnlyField(
        source='assigned_by.get_full_name')  # TODO fix this

    class Meta:
        model = TransactionAssignment
        fields = ('transaction', 'assigned_department',
                  'assigned_person', 'assigned_by')


class InspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inspection
        fields = '__all__'
