from django import forms
from .models import Comment

class EmailPostForm(forms.Form):
     name = forms.CharField(max_length=25)#будет использоваться для имени человека
     email = forms.EmailField()#используется адрес электронной почты человека, отправившего рекомендуемый пост
     to = forms.EmailField()
     comments = forms.CharField(required=False, widget=forms.Textarea)

class CommentForm(forms.ModelForm):
      class Meta:
           model = Comment
           fields = ['name', 'email', 'body']

class SearchForm(forms.Form):
     query = forms.CharField()
