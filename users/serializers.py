from django.contrib.auth.models import User, Group
from rest_framework import serializers

from users.models import Party, Property, StaffUser, Transaction, TransactionAssignment, Inspection


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email',]


class CustomerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        # fields = '__all__'
        fields = (
            'id',
            'first_name',
            'middle_name',
            'last_name',
            'identification',
            'email',
            'phone_number',
            'dob',
            'gender',
            'address',
            'city',
            'post_code',
            'natural_person',
            'citizenship',
        )


class StaffUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffUser
        # fields = '__all__'
        fields = (
            'id',
            'first_name',
            'middle_name',
            'last_name',
            'email',
            'phone_number',
            'department',
            'employee_id',
        )


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer class for Property Transaction
    """

    property = PropertySerializer()
    transferor = CustomerUserSerializer(many=True, read_only=True)
    transferee = CustomerUserSerializer(many=True, read_only=True)

    creator = serializers.ReadOnlyField(source='created_by.email')
    creator_id = serializers.ReadOnlyField(
        source='created_by.get_full_name')  # it was phone_number previously

    class Meta:
        model = Transaction
        fields = '__all__'
        # fields = ('id', 'type', 'form_number', 'registration_number', 'property', 'file_path',
        #           'purchase_price', 'received_from', 'transferee', 'transferor', 'notes', 'creator', 'creator_id',)
        read_only_fields = ["created_at", "created_by",]

    def create(self, validated_data):
        property_data = validated_data.pop('property')

        # create a new property
        property = Property.objects.create(**property_data)

        # create a new transaction
        transaction = Transaction.objects.create(
            property=property, **validated_data)
        return transaction

    def update(self, instance, validated_data):
        property_data = validated_data.pop('property')

        property = instance.property

        for attr, value in property_data.items():
            setattr(property, attr, value)
        property.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class TransactionAssignmentSerializer(serializers.ModelSerializer):

    assigned_person = serializers.ReadOnlyField(
        source='assigned_to.get_full_name',)
    assigned_department = serializers.ReadOnlyField(
        source='assigned_to.department')
    assigned_by = serializers.ReadOnlyField(
        source='assigned_by.get_full_name')  # TODO fix this

    class Meta:
        model = TransactionAssignment
        fields = (
            'transaction',
            'assigned_department',
            'assigned_person',
            'assigned_by'
        )


class InspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inspection
        fields = '__all__'
