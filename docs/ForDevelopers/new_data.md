---
layout: default 
title: New data type 
parent: For Developers 
nav_order: 1
---

This section will explain how additional data type can be added to the framework.

Be careful to note that this is intimately linked to the preprocessing/features step (see [New features](/ForDevelopers/new_features.html/) section for more information).


# Form implementation

## Data Choice
First, you need to add a tuple in the form `(acronym, full name)` to the `alambic_app > constantes.py` script in the list of the data choice `DATA_CHOICES`.

This operation will allow your data to be chosen during the import phase and be referenced in the downstream tasks.

## Parametrization
Per se, Data types do not have a form to implement. The `GeneralInfoInputForm` in the file `alambic_app > forms > forms.py` can be modified to add check in the file used for import if needed.

However, a form for the features has to be given according to the data type.

You need then to create a form in the folder `alambic_app > forms > data` for your type of data with the preprocessing steps and features than czn be applied on your data type.

Once created, the form has to be added to the `__init__.py` script of the folder for import.

Finally, you have to add the correspondence between the `acronym` selected in the previous step and its form in the function `get_form_data` in the `alambic_app > utils > data_management.py` script.

This will allow your form to be shown for the features/preprocessing setup step.

# Data implementation

## Location
New data type must be implemented in the `alambic_app > models > input_models.py`, as a child class of `Data`. The name of the class must match the `full name` chosen earlier in [Data Choice](/ForDevelopers/new_data.html#data-choice).

As you created a new model in the django database, you will have to migrate the changes with the following commands :

{% highlight bash %}
python manage.py makemigrations
python manage.py migrate
{% endhighlight %}

in the attached docker environment. More information on Django migrations, see [here](https://docs.djangoproject.com/en/4.0/topics/migrations/).

You only need to do the `migrate` command once to test the migration, as there is a `migrate` command during the launch of the ALAMBIC docker.

## Import of the data
If needed, you can specify how the data has to be imported in the function `upload_form_data` of the file `alambic_app > tasks.py`.

# Documentation
Update the documentation ! It is present in the folder `docs` in the `import.md` document.

# Checklist
- [ ] Add the (acronym, full name) tuple in the DATA_CHOICES list in the constantes.py script
- [ ] (Opt.) Modifiy the GeneralInfoInputForm in alambic_app > forms > forms.py to add any check of the import file as needed.
- [ ] Create a form in alambic_app > forms > data folder for the processing/features linked to the data
- [ ] Add the form in the init script for import
- [ ] Add the acronym and form correspondence in the function get_form_data in alambic_app > utils > data_management.py
- [ ] Implement a Django model for the data in alambic_app > models > input_models.py, as a child of the Data class
- [ ] Migrate the changes to the database
- [ ] (Opt.) Modify the upload_form_data of the file alambic_app > tasks.py
- [ ] Update the documentation (it's important too !)
- [ ] Be proud of yourself, you did it ! (Well, after tons of debug and testing, of course)