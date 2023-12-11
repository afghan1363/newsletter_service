from django import forms
from django.forms import DateInput

from newsletter_app.models import Client, Newsletter, Options


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'is_current' and field_name != 'is_published':
                field.widget.attrs['class'] = 'form-control'


class ClientForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Client
        # fields = '__all__'
        exclude = ('owner',)


class NewsletterForm(StyleFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(NewsletterForm, self).__init__(*args, **kwargs)

        # Ограничиваем queryset для выбора клиентов только теми, которых создал текущий пользователь
        self.fields['client'].queryset = Client.objects.filter(owner=user)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    class Meta:
        model = Newsletter
        fields = '__all__'


class OptionsForm(StyleFormMixin, forms.ModelForm):

    class Meta:
        model = Options
        fields = '__all__'
        widgets = {
            'date_start': DateInput(
                attrs={'type': 'date'}
            )
        }
