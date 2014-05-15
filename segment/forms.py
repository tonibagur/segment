# -*- coding: utf-8 -*-
from django import forms
from models import Image, Segment,Tag,ImageType
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator

class ImageForm(ModelForm):
    class Meta:
        model = Image
        fields = ['name', 'filename', 'image_type']

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(ImageForm, self).__init__(*args, **kwargs)
        self.fields['image_type'].queryset = ImageType.objects.filter(users_shared=self.user).order_by('name')



class SegmentForm(ModelForm):
    x1 = forms.FloatField(widget=forms.HiddenInput())
    y1 = forms.FloatField(widget=forms.HiddenInput())
    x2 = forms.FloatField(widget=forms.HiddenInput())
    y2 = forms.FloatField(widget=forms.HiddenInput())
    class Meta:
        model = Segment
        fields = ['x1','x2','y1','y2','image','tags','filename']

    def __init__(self, *args, **kwargs):
       super(SegmentForm, self).__init__(*args, **kwargs)
       #Filtrem tags del segment segons el tipo de imatge al que pertanyen
       if 'instance' in kwargs and kwargs['instance'].image.image_type.id:
           image_type_filter = kwargs['instance'].image.image_type.id
           self.fields['tags'].queryset = Tag.objects.filter(image_type=image_type_filter).order_by('name')

class GenerateImagesForm(forms.Form):
    image_type = forms.ModelChoiceField(queryset=ImageType.objects.all())
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all().order_by('name'))

    def __init__(self, user=None, image=None,*args, **kwargs):
        self.user = user
        super(GenerateImagesForm, self).__init__(*args, **kwargs)
        self.fields['image_type'].queryset = ImageType.objects.filter(users_shared=self.user).order_by('name')
        image_type_filter = ImageType.objects.filter(id=image.image_type.id).order_by('name')
        self.fields['tags'].queryset = Tag.objects.filter(image_type=image_type_filter).order_by('name')

class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class PassworResetForm(forms.Form):
    error_messages = {
        'unknown': ("That email address doesn't have an associated "
                     "user account. Are you sure you've registered?"),
        'unusable': ("The user account associated with this email "
                      "address cannot reset the password."),
        }
    def clean_email(self):
        """
        Validates that an active user exists with the given email address.
        """
        UserModel = get_user_model()
        email = self.cleaned_data["email"]
        self.users_cache = UserModel._default_manager.filter(email__iexact=email)
        if not len(self.users_cache):
            raise forms.ValidationError(self.error_messages['unknown'])
        if not any(user.is_active for user in self.users_cache):
            # none of the filtered users are active
            raise forms.ValidationError(self.error_messages['unknown'])
        if any((user.password == UNUSABLE_PASSWORD)
            for user in self.users_cache):
            raise forms.ValidationError(self.error_messages['unusable'])
        return email

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        from django.core.mail import send_mail
        for user in self.users_cache:
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            c = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': int_to_base36(user.pk),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': use_https and 'https' or 'http',
                }
            subject = loader.render_to_string(subject_template_name, c)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            email = loader.render_to_string(email_template_name, c)
            send_mail(subject, email, from_email, [user.email])













