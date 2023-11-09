from django.contrib.auth.models import User, Group
from rest_framework import serializers

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
    property = PropertySerializer()
    transferor = PartySerializer(many=True, read_only=True)
    transferee = PartySerializer(many=True, read_only=True)
    # creator_name = serializers.ReadOnlyField(
    #     source='created_by.get_full_name')

    class Meta:
        model = Transaction
        # fields = '__all__'
        fields = ('id',
                  'type',
                  'form_number',
                  'registration_number',
                  'property',
                  'purchase_price',
                  'received_from',
                  'transferee',
                  'transferor',
                  'notes',
                  'created_at',
                  )


class WriteTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer class for Property Transaction
    """

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
                  'notes',
                  )
        read_only_fields = ["created_at", "created_by",]
        # exclude = ['creator_id']

    def create(self, validated_data):
        property_data = validated_data.pop('property', {})
        transferors_data = validated_data.pop('transferor', [])
        transferees_data = validated_data.pop('transferee', [])

        # Try to find an existing Property instance based on provided data
        matching_properties = Property.objects.filter(**property_data)

        if matching_properties.exists():
            # If matching properties exist, use the first one
            property_instance = matching_properties.first()
        else:
            # If no matching properties exist, create a new one
            property_instance = Property.objects.create(**property_data)

        transaction = Transaction.objects.create(
            property=property_instance, **validated_data)

        for transferor_data in transferors_data:
            transferor = Party.objects.create(**transferor_data)
            transaction.transferor.add(transferor)

        for transferee_data in transferees_data:
            transferee = Party.objects.create(**transferee_data)
            transaction.transferee.add(transferee)

        return transaction

    def update(self, instance, validated_data):
        property_data = validated_data.pop('property', {})
        transferors_data = validated_data.pop('transferor', [])
        transferees_data = validated_data.pop('transferee', [])

        # Update transaction fields
        instance.__dict__.update(validated_data)
        instance.save()

        # Update the related property instance
        property_instance = instance.property
        if property_instance:
            PropertySerializer(propoertyinstance, data=property_data)
            property_instance.save()

        # Update the related transferor instances
        for transferor_data in transferors_data:
            if 'id' in transferor_data:
                transferor = Party.objects.get(id=transferor_data['id'])
                PartySerializer(transferor, data=transferor_data).update(
                    transferor, transferor_data)
            else:
                instance.transferor.create(**transferor_data)

        # Update the related transferee instances
        for transferee_data in transferees_data:
            if 'id' in transferee_data:
                transferee = Party.objects.get(id=transferee_data['id'])
                PartySerializer(transferee, data=transferee_data).update(
                    transferee, transferee_data)
            else:
                instance.transferee.create(**transferee_data)

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
