---
layout: default 
title: Analysis of query strategies 
parent: Choice of the active learning task 
grand_parent: How to use ALAMBIC 
nav_order: 3
---

# Parameters

## Query strategies
You select any number of currently implemented query strategies (see [here](/Tutorials/query_strategy.html/) for their list) to analyse.

## Cross-validation
Cross-validation is a resampling method that uses different portions of the data to test and train a model on different iterations. The dataset is partitioned into complementary subsets, where the data is trained on one subset and its performance is evaluated on the other. Performance is averaged over several rounds of cross-validations.

In this case, we implement a k-fold cross-validation, meaning that the dataset is split in k parts, where for each round one part is considered as the test set and all the other k-1 parts are combined as the training set.

Minimum value of 5.

## Ratio seed
Portion of the dataset considered as the starting training set.

Value between 0.1 and 1.

## Repeats
Number of times the learning process is repeated with the same test set, so as to reduce the variability introduced by the initial labelled training set.

Minimum value of 1.
