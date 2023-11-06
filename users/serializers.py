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


class ReadTransactionSerializer(serializers.ModelSerializer):
    property = PropertySerializer()
    transferor = CustomerUserSerializer(many=True, read_only=True)
    transferee = CustomerUserSerializer(many=True, read_only=True)
    creator_name = serializers.ReadOnlyField(
        source='created_by.get_full_name')

    class Meta:
        model = Transaction
        # fields = '__all__'
        fields = ('id',
                  'type',
                  'form_number',
                  'registration_number',
                  'property',
                  'file_path',
                  'purchase_price',
                  'received_from',
                  'transferee',
                  'transferor',
                  'notes',
                  'creator_name'
                  'created_at',
                  )


class WriteTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer class for Property Transaction
    """

    property = PropertySerializer()
    transferor = CustomerUserSerializer(many=True)
    transferee = CustomerUserSerializer(many=True)

    class Meta:
        model = Transaction
        fields = ('id',
                  'type',
                  'form_number',
                  'registration_number',
                  'property',
                  'file_path',
                  'purchase_price',
                  'received_from',
                  'transferee',
                  'transferor',
                  'notes',
                  )
        read_only_fields = ["created_at", "created_by",]
        # exclude = ['creator_id']

    def to_internal_value(self, data):
        property_data = data.pop('property', {})
        transferors_data = data.pop('transferor', [])
        transferees_data = data.pop('transferee', [])

        instance = super().to_internal_value(data)

        if 'property' in instance:
            property_instance = instance.pop('property')
            PropertySerializer(property_instance, data=property_data).save()

        for transferor_data in transferors_data:
            if 'id' in transferor_data:
                transferor = Party.objects.get(id=transferor_data['id'])
                CustomerUserSerializer(transferor, data=transferor_data).save()
            else:
                instance.transferor.create(**transferors_data)

        for transferee_data in transferees_data:
            if 'id' in transferee_data:
                transferee = Party.objects.get(id=transferee_data['id'])
                CustomerUserSerializer(transferee, data=transferee_data).save()
            else:
                instance.transferee.create(**transferees_data)

        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['property'] = PropertySerializer(instance.property).data

        data['transferor'] = CustomerUserSerializer(
            instance.transferor.all(), many=True).data
        data['transferee'] = CustomerUserSerializer(
            instance.transferee.all(), many=True).data

        return data


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
