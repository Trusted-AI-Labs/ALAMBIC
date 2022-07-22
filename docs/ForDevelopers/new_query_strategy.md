---
layout: default 
title: New query strategy 
parent: For Developers 
nav_order: 4
---

# Form implementation

## Strategy Choice
First, you need to add a tuple in the form `(acronym, full name)` to the `alambic_app > constantes.py` script in the list of the strategy choice `AL_ALGORITHMS_CHOICES`, as well in the form of a `acronym: full name` entry in the dictionary `AL_ALGORITHMS_MATCH`.

This operation will allow your strategy to be chosen during the setup phase, as well as showing the full name in the plots.

## Parametrization
Currently, the query strategies do not have parametrization available. Thus, no additional form are necessary.

# Strategy implementation
## Preface
Our framework is currently based on the library `ALiPy` (repository [here](https://github.com/NUAA-AL/ALiPyhttps://github.com/NUAA-AL/ALiPy)).

Additional strategy must be built with the `BaseQueryIndex` class from that vvery same library and implement the `select` method.

## Location
Implemented strategies must be implemented in the `alambic_app > active_learning > strategies.py` file.

Once implemented, the model must be imported and added to the `AL_ALGORITHMS_MATCH` dictionary in the `alambic_app > machine_learning > setup.py` script with their corresponding `acronym` (see Strategy Choice in the previous section).

## Parametrization
If specific parameters must be added to the strategy, you can add the code in the `alambic_app > machine_learning > setup.py` script, in the `set_query_strategy` method.

# Documentation
Update the documentation ! It is present in the folder `docs` in the `query_strategy.md` document.

# Checklist
- [ ] Add the (acronym, full name) tuple in the AL_ALGORITHMS_CHOICES list and the dictionary AL_ALGORITHMS_MATCH in the constantes.py script
- [ ] (Opt.) Implement the strategy if not existing in the alambic_app > active_learning > strategies.py file.
- [ ] Import in alambic_app > machine_learning > setup.py and add to AL_ALGORITHMS_MATCH with the acronym as key and the model function as value
- [ ] Modify the set_query_strategy method if needed for the parameters of the strategy.
- [ ] Update the documentation (it's important too !)
- [ ] Be proud of yourself, you did it ! (Well, after tons of debug and testing, of course)