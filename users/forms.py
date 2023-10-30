from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser, Party, StaffUser


class StaffUserCreationForm(UserCreationForm):

    class Meta:
        model = StaffUser
        fields = ("email",)


class StaffUserChangeForm(UserChangeForm):

    class Meta:
        model = StaffUser
        fields = ("email",)
      

class PartyUserCreationForm(UserCreationForm):

    class Meta:
        model = Party
        fields = ("email",)


class PartyUserChangeForm(UserChangeForm):

    class Meta:
        model = Party
        fields = ("email",)
