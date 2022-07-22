---
layout: default 
title: New features 
parent: For Developers 
nav_order: 3
---
This section will explain how additional features can be added to the framework.

Be careful to note that features are generally linked to the Data type (see [New data](/ForDevelopers/new_data.html)).

# Form implementation

## Features Choice
First, you need to add a tuple in the form `(acronym, full name)` to the `alambic_app > constantes.py` script in the corresponding list of the data preprocessing and features choice, according to the fact if your new features is one or the other, for example `PREPROCESSING_TEXT_CHOICES` and `FEATURES_TEXT_CHOICES` are for the text data.

This operation will link your new features to the data type and make it available to the user when setting up the process.

## Parametrization
New features must be added to the form of the corresponding data type they can be used with in the folder `alambic_app > forms > data`.

It should be noted that initial preprocessing steps must be put before the features in order for the pipeline to work correctly.

This operation will add the features in the front end without any additional steps.

# Features implementation

## Location
If needed, new features should be implemented in the script with the name corresponding to their related data type (e.g. `text.py`) in the folder `alambic_app > features`.

Once implemented, the features must be imported and added to the `OPERATIONS_MATCH` dictionary in the `alambic_app > machine_learning > setup.py` script with their corresponding `acronym` (see [Features Choice](/ForDevelopers/new_features.html#features-choice) in the previous section).

Features from existing libraries (such as sklearn) can simply be directly imported and included in the dictionary with their corresponding `acronym`.

If the feature is custom and do not follow the structure of the functions in sklearn in order to be included in a pipeline (see [Pipeline in sklearn](https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html), their acronym must be added to the set of `CUSTOM_FUNCTIONS` so that they can be transformed to be used as such.

## Parametrization
If specific parameters must be added to the features process (outside to what can be selected in a form), you can add the code in the `alambic_app > machine_learning > preprocessing.py` script, in the `get_pipeline` method.

# Documentation
Update the documentation ! It is present in the folder `docs` in the `features.md` document.

# Checklist
- [ ] Add the (acronym, full name) tuple in the PREPROCESSING_DATA_CHOICES or FEATURES_DATA_CHOICES list in the constantes.py script
- [ ] Add your features in the corresponding data form in the folder alambic_app > forms > data
- [ ] (Opt.) Implement the feature if not existing in the corresponding data script in the alambic_app > features folder and add the function to the init script
- [ ] Import in alambic_app > machine_learning > preprocessing.py and add to OPERATIONS_MATCH with the acronym as key and the feature function as value
- [ ] (Opt.) If custom function, add the acronym of the function to the CUSTOM_FUNCTIONS set
- [ ] Modify the get_pipeline method if needed for the parameters of the features.
- [ ] Update the documentation (it's important too !)
- [ ] Be proud of yourself, you did it ! (Well, after tons of debug and testing, of course)