---
layout: default 
title: Query strategies 
parent: Choice of the active learning task 
grand_parent: How to use ALAMBIC 
nav_order: 1
math: mathjax2
---

# Overview 
Active learning query strategies were implemented by the library ALiPy ([documentation](http://parnec.nuaa.edu.cn/huangsj/alipy/)).

We decided to currently integrate query strategies :
- for instance selection
- which do not require more than the developed model

# Currently available strategies
## Random sampling
Base method used to compare with the performance of other query strategies. It just selects the required number of queries in a random manner.

## Uncertainty sampling
The uncertainty sampling is the way the learner will select queries for whom it is the most uncertain in their label. This uncertainty can be measured in different ways.

Let's define $$x$$ as an instance, $$\hat{y_i}$$ corresponds to the $$i$$th most likely class predicted for the the instance $$x$$.

### Least confident
The simplest measure calculate the difference between 100% confidence and the most confident prediction obtained for the instance $$x$$
$$LC(x) = 1 - P(\hat{y_1}|x)$$

### Margin
Calculates the difference between the top two most confident predictions.

$$M(x) = P(\hat{y_1}|x) - P(\hat{y_2}|x)$$

In that case, the strategy will select the instance with the smallest margin, since the smaller the margin is, the most unsure the decision.

### Entropy
Calculates the difference between all the prediction, as defined by information theory.

$$H(x) = -\sum_{k}P(y_k|x)\log(P(y_k|x))$$
