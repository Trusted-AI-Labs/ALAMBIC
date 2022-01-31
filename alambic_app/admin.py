from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter

from alambic_app.models.input_models import *


# Register your models here.

@admin.register(Data)
class DataParentAdmin(PolymorphicParentModelAdmin):
    """
    Parent admin model for data to show all data types from the same list view.
    Defined as suggested by the `Django Polymorphic documentation <https://django-polymorphic.readthedocs.io/en/stable/admin.html>`_
    """
    child_models = (Image, Text)
    polymorphic_list = True

    list_display = (
        'id',
        'filename'
    )

    search_fields = ('id', 'filename')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_filter = [PolymorphicChildModelFilter]
        self.readonly_fields = ['id']

    def data_type(self, obj):
        return type(obj).__name__


class DataChildAdmin(PolymorphicChildModelAdmin):
    """
    Child model admin that is used as base class by the concrete admin classes for variants
    """

    search_fields = ('id', 'filename')

    def add_view(self, request, form_url='', extra_context=None):
        self.exclude = self.readonly_fields.copy()
        self.readonly_fields = []
        return super().add_view(request, form_url, extra_context)


@admin.register(Image)
class ImageAdmin(DataChildAdmin):
    """
    Child model admin for SmallVariant variants
    """
    base_model = Image


@admin.register(Text)
class TextAdmin(DataChildAdmin):
    """
    Concrete model admin for CopyNumberVariant variants
    """
    base_model = Text


@admin.register(Output)
class OutputAdmin(admin.ModelAdmin):
    list_display = (
        'data',
        'label',
        'annotated_by_human'
    )
