from django import forms

class FileForm(forms.Form):
    file = forms.FileField(label="Select file")
    model_weights = forms.FileField(label="Select model weights file")


    