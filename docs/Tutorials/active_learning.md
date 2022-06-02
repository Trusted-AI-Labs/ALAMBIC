---
layout: default 
title: Choice of the active learning task 
parent: How to use ALAMBIC 
has_children: true 
nav_order: 4
---

# Overview
With ALAMBIC, you can either develop a model with the help of active learning, meaning that you can also label in an optimized way (according to your chosen strategy) your data at the same time as you train a chosen model, or you can analyse the impact of different query strategies on the performance of a model.


# Which one should I choose ?
If you are working with a partially labelled dataset and you want to label the rest, while still optimizing the amount of labels you have to provide, then developing a model is the task to choose. The obtained labels are enriching your dataset and the obtained model can label the rest of your data with a specified accuracy based on the given information.

If you want to study which query strategy would be more convenient for your dataset (prior to the task of developing a model, for example), or you want to compare the performance of a new query strategy your developed with other commonly used query strategies, then the analysis task is the way to go.

<h2>Note on the analysis of query strategies <p class="label label-red">Important</p> </h2>
In order to be performed successfully, the analysis must be performed with a dataset fully labelled preferably.

# Batch size
You will have to choose the size of the batch of queries which will be selected by your learner after each training and inference.

A large batch size has the advantage of labelling more examples at once, thus reducing the delay we have due to the tedious process of having to retrain everytime after we add the newly labelled queries to the labelled dataset. However, it also means that your leaner will have to select a higher number of labels with less information than what he should have. That means that if you have to select 100 queries, those queries will be chosen only based on the currently known labels, while knowing the 99 previous labels could lead the learner to select a complete different 100th query.

On another hand, this could be also a parameter to test in the case of the analysis task.

More information and discussion found on [this github website](https://dsgissin.github.io/DiscriminativeActiveLearning/2018/07/05/Batch-AL.html). You can also find different strategies affecting the batch size.

# The process
Once you have chosen either the analysis or the model development, you can submit and everything will be launched.

You can keep track of the progress of the process on the `/distilling` page where it indicates if the learner is either training, predicting or selecting a query.

You won't have anything to do except label queries if the label is not available in the development mode (See [Annotation](/Tutorials/annotation.html/) for more information)
