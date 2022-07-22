---
layout: default 
title: New model 
parent: For Developers 
nav_order: 2
---

This section will explain how additional models can be added to the framework.

# Form implementation
For the model to be used, the frontend needs to have access to different forms in order to choose the model and parameterize it.

## Model Choice
First, you need to add a tuple in the form `(acronym, full name)` to the `alambic_app > constantes.py` script in the corresponding list of the task model choice, for example `CLASSIFICATION_MODELS_CHOICES` is for the classification task.

This operation will allow your model to be chosen for the related task.

## Parametrization
You need then to create a form in the folder corresponding to your task in `alambic_app > forms > task`, for example in the `classification` folder if your model can be used for classification.

The goal of this form is to offer to the user access to the relevant parameters of the model.

Once created, the form has to be added to the `__init__.py` script of the folder for import.

Finally, you have to add the correspondence between the `acronym` selected in the previous step and its form in the function `get_form_model` in the `alambic_app > utils > data_management.py` script.

This will allow your form to be shown after the model was chosen by the user.

# Model implementation
## Preface
Additional models must have the `fit` and `predict` methods implemented, the first one receiving `X, Y` as arguments and the second only `X`, where `X` corresponds to a numpy array of features of shape `(features, n_samples)` and `Y` corresponding to the labels of the given `X` array.

## Location
Implemented models must be implemented in the `alambic_app > machine_learning` folder.

Once implemented, the model must be imported and added to the `MODELS_MATCH` dictionary in the `alambic_app > machine_learning > setup.py` script with their corresponding `acronym` (see Model Choice in the previous section).

Models from existing librairies (such as models in sklearn) can simply be directly imported.

## Parametrization
If specific parameters must be added to the model (outside to what can be selected in a form, see next section), you can add the code in the `alambic_app > machine_learning > setup.py` script, in the `create_model` method.

# Documentation
Update the documentation ! It is present in the folder `docs` as children of the `machine_learning.md` document.

# Checklist
- [ ] Add the (acronym, full name) tuple in the TASK_MODELS_CHOICES list in the constantes.py script
- [ ] Create a form in alambic_app > forms > task folder with the parameters of the model
- [ ] Add the form in the init script for import
- [ ] Add the acronym and form correspondence in the function get_form_model in alambic_app > utils > data_management.py
- [ ] (Opt.) Implement the model if not existing in the alambic_app > machine_learning folder.
- [ ] Import in alambic_app > machine_learning > setup.py and add to MODELS_MATCH with the acronym as key and the model function as value
- [ ] Modify the create_model method if needed for the parameters of the model.
- [ ] Update the documentation (it's important too !)
- [ ] Be proud of yourself, you did it ! (Well, after tons of debug and testing, of course)