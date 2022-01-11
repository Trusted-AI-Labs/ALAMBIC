# ALAMBIC
Django framework for active learning tasks, inspiration from [iepy](https://github.com/machinalis/iepy/) and [ORVAL](https://github.com/oligogenic/ORVAL/)

## Structure proposed :

- machine_learning for the machine learning models implementation (training and prediction)
- active_learning for the query strategies and user inquiry (and eventually the strategy for the model
  retraining/correction ?)
- annotations for importing the data, the user annotation/labelling part, all the different tasks (classification, image
  labelling, text annotation, etc.)
  - text-mining (relationship extraction, NER)
  - Image labelling (?)
  - Classification
- plots for all the analyses that can be done during active learning

---

## TO DO

- [ ] Implement feature extraction and
  preprocessing (https://scikit-learn.org/stable/modules/preprocessing.html#preprocessing)
  - [ ] In the ML pipeline
  - [ ] In the form as parameters
- [ ] Implement model choices + parameters (focus on classification at the moment)
- [ ] Write and implement the annotation part
  - [ ] Plots
  - [ ] Submission annotation
- [ ] Download results
- [ ] Download annotation

---

## Reflexions

- NLP Spark looks really nice for text-mining tasks, but would need Apache spark installed, there is a docker
  version : https://nlp.johnsnowlabs.com/docs/en/install#docker-support
- Focus at the moment on classification, but do the Relationship extraction as fast as possible