from django import forms
from .models import (
    GPU, CPU, RAM, Motherboard, Case, StorageDevice, 
    PSU, Monitor, Mouse, Keyboard, Headset, Speakers, 
    OtherAccessory, Tablet, Laptop, Subscriber, ContactMessage
)

class GPUForm(forms.ModelForm):
    class Meta:
        model = GPU
        fields = '__all__'
        exclude = ['sku']  # SKU is auto-generated

class CPUForm(forms.ModelForm):
    class Meta:
        model = CPU
        fields = '__all__'
        exclude = ['sku']

class RAMForm(forms.ModelForm):
    class Meta:
        model = RAM
        fields = '__all__'
        exclude = ['sku']

class MotherboardForm(forms.ModelForm):
    class Meta:
        model = Motherboard
        fields = '__all__'
        exclude = ['sku']

class CaseForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = '__all__'
        exclude = ['sku']

class StorageDeviceForm(forms.ModelForm):
    class Meta:
        model = StorageDevice
        fields = '__all__'
        exclude = ['sku']

class PSUForm(forms.ModelForm):
    class Meta:
        model = PSU
        fields = '__all__'
        exclude = ['sku']

class MonitorForm(forms.ModelForm):
    class Meta:
        model = Monitor
        fields = '__all__'
        exclude = ['sku']

class MouseForm(forms.ModelForm):
    class Meta:
        model = Mouse
        fields = '__all__'
        exclude = ['sku']

class KeyboardForm(forms.ModelForm):
    class Meta:
        model = Keyboard
        fields = '__all__'
        exclude = ['sku']

class HeadsetForm(forms.ModelForm):
    class Meta:
        model = Headset
        fields = '__all__'
        exclude = ['sku']

class SpeakersForm(forms.ModelForm):
    class Meta:
        model = Speakers
        fields = '__all__'
        exclude = ['sku']

class OtherAccessoryForm(forms.ModelForm):
    class Meta:
        model = OtherAccessory
        fields = '__all__'
        exclude = ['sku']

class TabletForm(forms.ModelForm):
    class Meta:
        model = Tablet
        fields = '__all__'
        exclude = ['sku']

class LaptopForm(forms.ModelForm):
    class Meta:
        model = Laptop
        fields = '__all__'
        exclude = ['sku']

class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'input-group__field newsletter__input',
                'placeholder': 'Email address',
                'required': True
            })
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Subscriber.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already subscribed to our newsletter.")
        return email

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'ggt-contact-form-control',
                'placeholder': 'Your Name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'ggt-contact-form-control',
                'placeholder': 'Your Email',
                'required': True
            }),
            'subject': forms.TextInput(attrs={
                'class': 'ggt-contact-form-control',
                'placeholder': 'Subject',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'ggt-contact-form-control',
                'placeholder': 'Your Message',
                'required': True,
                'rows': 5
            }),
        } 