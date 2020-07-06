from .models import Shop,Category,District
import django_filters

class ShopFilter(django_filters.FilterSet):
    # district = django_filters.ModelChoiceFilter(queryset=District.objects.all())
    class Meta:
        model = Shop
        fields = ['category','district']
