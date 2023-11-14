from django.contrib.auth.models import User, Group
from rest_framework import serializers
from django.db import transaction
# from drf_extra_fields.fields import Base64FileField

from users.models import Party, Property, StaffUser, Transaction, TransactionAssignment, Inspection


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email',]


class PartySerializer(serializers.ModelSerializer):
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


class ReadTransactionSerializer(serializers.ModelSerializer):
    file_path = Base64FileField(required=False)
    property = PropertySerializer(read_only=True)
    transferor = PartySerializer(many=True, read_only=True)
    transferee = PartySerializer(many=True, read_only=True)
    # creator_name = serializers.ReadOnlyField(
    #     source='created_by.get_full_name')

    class Meta:
        model = Transaction
        fields = ('id',
                  'type',
                  'form_number',
                  'registration_number',
                  'property',
                  'purchase_price',
                  'received_from',
                  'transferee',
                  'transferor',
                  'file_path',
                  'notes',
                  'created_at',
                  )


class WriteTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer class for Property Transaction
    """
    file_path = Base64FileField(required=False)

    property = PropertySerializer()
    transferor = PartySerializer(many=True)
    transferee = PartySerializer(many=True)

    class Meta:
        model = Transaction
        fields = ('id',
                  'type',
                  'form_number',
                  'registration_number',
                  'property',
                  'purchase_price',
                  'received_from',
                  'transferee',
                  'transferor',
                  'file_path',
                  'notes',
                  )
        read_only_fields = ["created_at", "created_by",]
        # exclude = ['creator_id']

    def create(self, validated_data):
        property_data = validated_data.pop('property', {})
        transferors_data = validated_data.pop('transferor', [])
        transferees_data = validated_data.pop('transferee', [])

        with transaction.atomic():
            property_instance, _ = Property.objects.get_or_create(
                **property_data)
            my_transaction = Transaction.objects.create(
                property=property_instance, **validated_data)

            for transferor_data in transferors_data:
                transferor, _ = Party.objects.get_or_create(**transferor_data)
                my_transaction.transferor.add(transferor)

            for transferee_data in transferees_data:
                transferee, _ = Party.objects.get_or_create(**transferee_data)
                my_transaction.transferee.add(transferee)

        return my_transaction

    def update(self, instance, validated_data):
        # Update fields of the Transaction model
        instance.type = validated_data.get('type', instance.type)
        instance.form_number = validated_data.get(
            'form_number', instance.form_number)
        instance.registration_number = validated_data.get(
            'registration_number', instance.registration_number)
        instance.purchase_price = validated_data.get(
            'purchase_price', instance.purchase_price)
        instance.received_from = validated_data.get(
            'received_from', instance.received_from)
        instance.notes = validated_data.get('notes', instance.notes)

        # Update the Property instance
        property_data = validated_data.get('property', {})
        property_instance, _ = Property.objects.get_or_create(**property_data)
        instance.property = property_instance

        # Update transferors
        transferors_data = validated_data.get('transferor', [])
        instance.transferor.clear()
        for transferor_data in transferors_data:
            transferor, _ = Party.objects.get_or_create(**transferor_data)
            instance.transferor.add(transferor)

        # Update transferees
        transferees_data = validated_data.get('transferee', [])
        instance.transferee.clear()
        for transferee_data in transferees_data:
            transferee, _ = Party.objects.get_or_create(**transferee_data)
            instance.transferee.add(transferee)

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
