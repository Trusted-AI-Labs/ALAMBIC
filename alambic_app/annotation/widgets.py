from django_select2.forms import ModelSelect2TagWidget

from alambic_app.models.labels import ClassificationLabel
from alambic_app.utils.exceptions import ParsingError


class SelectOrCreateWidget(ModelSelect2TagWidget):
    allow_multiple_selected = False  # Small hack to get a tag widget that is normal

    error = None

    new_added = False
    new_pk = None

    def __init__(self, *args, user=None, is_submit=True, **kwargs):
        self.user = user  # Add user for parsing variants, as we need a submitter for new DB instances
        self.is_submit = is_submit
        # kwargs['attrs'] = {"data-token-separators": '[","]'}# Attrs to allow whitespace in tokens
        super().__init__(*args, **kwargs)

    def set_user(self, user):
        self.user = user

    def create_instance(self, user_input):
        """
        Abstract method that should be implemented by subclasses to create a new instance from
        user input.

        :param input: User input from the widget search field
        :type input: str
        :raises NotImplementedError: Subclasse should implement
        """
        raise NotImplementedError

    def value_from_datadict(self, data, files, name):

        values = super().value_from_datadict(data, files, name)
        if self.new_added:
            # This check is necessary, as value_from_datadict gets called twice on each form submission
            return self.new_pk
        elif values and not values[0].isnumeric() and not 'new' in values:  # 'new' check for variants, ignored for
            # TODO: we might need to introduce a check that does not call this when going back in the form wizard, otherwise new disease are created from the previously added data
            try:
                return self.create_instance(values[0])
            except ParsingError as pe:
                print('Parsing error!')
                self.error = f'Could not parse string {values[0]} into a variant due to the following parsing error: {pe.message}'
                values = None
        # still need to check that values is not empty
        elif values:
            values = values[0]

        return values

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs=extra_attrs)
        attrs['data-token-separators'] = '[","]'
        return attrs


class ClassificationLabelModelSelect(SelectOrCreateWidget):
    """
    Widget that enables creation of a class label from the appropriate string input next to
    the default select2 enhancements.
    """

    model = ClassificationLabel
    queryset = ClassificationLabel.objects.all()
    search_fields = ['value__icontains']

    def create_instance(self, user_input):
        new_data = user_input

        if new_data is not None:
            # Copy relevant search keys to use in filter
            check_dict = {
                'value': new_data['value']
            }
            # the manager of the ClassificationLabel checks the existence and will return the existing one if it is found
            self.new_pk = self.model.objects.create_instance(**check_dict)
            return self.new_pk
