from dal import autocomplete

from django import forms

from point_and_clickle.games.models import Game


class TitleForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ('title',)
        widgets = {
            'title': autocomplete.ModelSelect2(url='games:game-autocomplete')
        }
