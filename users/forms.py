from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

""" создадим собственный класс для формы регистрации,
сделаем его наследником предустановленного класса UserCreationForm

"""

class CreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        
        """ укажем модель, с которой связана создаваемая форма """
        
        model = User
        
        """ укажем отображаемые поля в форме и их порядок """
        
        fields = ("first_name", "last_name", "username", "email")
