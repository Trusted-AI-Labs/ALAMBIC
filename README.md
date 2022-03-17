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

- [X] Analyse Active learning
  - [X] Plot performance
  - [X] Download results
- [X] Reimplementation of strategies with ALiPy
- [ ] (R)elation (E)xtraction
  - [ ] Separated of NER ?
  - [ ] Model for classification between identified entities
  - [ ] Import of Data

---

## References

- Tang, Y.-P.; Li, G.-X.; and Huang, S.-J. 2019. ALiPy: Active learning in python. Technical report, Nanjing University
  of Aeronautics and Astronautics. available as arXiv preprint https://arxiv.org/abs/1901.03802.
- Danka, T. and Horvath, P. 2018. modAL: A modular active learning framework for Python. available on arXiv
  at https://arxiv.org/abs/1805.00979.