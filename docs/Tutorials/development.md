---
layout: default 
title: Development of a model 
parent: Choice of the active learning task 
grand_parent: How to use ALAMBIC 
nav_order: 2
---
# Parameters
## Query Strategy
See the current available strategies [here](/Tutorials/query_strategy.html/).

## Ratio test
Portion of the dataset to be used to evaluate the performance of the dataset.

Value to choose between 0 and 1.

## Size seed
Number of samples to start the training with.

Value to choose between 1 and the number of samples in your dataset minus the portion of the dataset used for testing purposes.

## Stop criterion
The stop criterion is the criterion when the active learning loop will stop.

### Budget-based
The loop will stop once a specific number of samples have been labeled.

### Performance-based
The loop will stop once a minimal accuracy has been reached by the model.
