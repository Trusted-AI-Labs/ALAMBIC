# ALAMBIC
Django framework for active learning tasks, inspiration from [iepy](https://github.com/machinalis/iepy/) and [ORVAL](https://github.com/oligogenic/ORVAL/)

## Structure proposed :
- alambic_app for interface and views control
- machine_learning for the machine learning models implementation (training and prediction)
  - features extraction (?)
  - models (separate them according to task ? i.e. classification, regression, NN, etc. ?)
- active_learning for the query strategies and user inquiry (and eventually the strategy for the model retraining/correction ?)
- annotations for importing the data, the user annotation/labelling part, all the different tasks (classification, image labelling, text annotation, etc.)
  - text-mining (relationship extraction, NER)
  - Image labelling (?)
  - Classification
- plots for all the analyses that can be done during active learning
---
## To dockerize
See [here](https://docs.docker.com/samples/django/)

---
## Choices to make
- Celery or redis (celery would keep track of jobs, help for parallelization, etc.)
- apps or modules ? *modules*
- Upload included or separated from the pipeline ? *Separated*
- Upload :
  - Separate labeled and unlabeled data ? *Separated*
  - Abstract Model for Data Point (x,y)
    - Model for features (x) and for output (y)
    - Specialize according to input (inheritance) or specify in a field of the model ?
      - text
      - image
      - vector (already, the St Graal)
    - Specialize for output :
      - general :
        - classification
        - regression
      - text-specific :
        - NER (class + word position)
        - RE (set words position)