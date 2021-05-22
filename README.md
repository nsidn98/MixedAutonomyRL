# MixedAutonomyRL
Final Course Project for [6.884 Computational Sensorimotor Learning Spring 2021](https://pulkitag.github.io/6.884/)

## What is this project about?
Using Reinforcement Learning in mixed autonomus traffic scenarios to manage congestion. We look into the bottleneck environment (in the [Flow](https://github.com/flow-project/flow) + [SUMO](https://www.eclipse.org/sumo/) simulator) where the lanes merge from four to two to one. The objective is to maximise the overall throughput of the vehicles through the bottleneck.

### The bottleneck environment
![bottleneck](https://raw.githubusercontent.com/nsidn98/MixedAutonomyRL/main/figures/bottleneck.png?token=AGFGCMH7KRZY6AKAYZ6GRO3AWKCRW)
The lanes merge from four to two at edge-3 and from two to one at edge-4.

## Difference from previous works:
Previous works [[1]](http://proceedings.mlr.press/v87/vinitsky18a.html), [[2]](https://arxiv.org/abs/2011.00120) have focused on optimizing throughput through the bottleneck, with less focus on ensuring fairness in the optimal solution and assessing robustness to possible environmental variation. Thus, our project explores the impacts of explicitly considering fairness and more human driver variation while training the AVs on their throughput-increasing effects in the bottleneck environment.

## Addition of fairness
Previous work focused of learning RL policies in the bottleneck environment without any fairness considerations. As seen in figures below, this results in the controller learning a policy which blocks some lanes and reserves a high throughput to maximize the average throughput through the bottleneck. To avoid learning similar behaviour, we define fairness as all vehicles spending similar amounts of time in the bottleneck - e.g. all vehicles traveling through the bottleneck at approximately the same speed, no matter which lane they are in. We add fairness considerations to training through reward shaping. More specifically, we add a fairness penalty to the rewards (refer [report](https://github.com/nsidn98/MixedAutonomyRL/blob/main/MA_fairness.pdf) for more details).

* Behaviour learnt when training without regard for fairness: Autonomous vehicles (red) learn to block the upper lanes in order to reserve the lower lane as a high-throughput lane;
![no_fair](https://raw.githubusercontent.com/nsidn98/MixedAutonomyRL/main/figures/noFair2.png?token=AGFGCMAUOHN3QCRAHLZGPTLAWKDSK)

* Behaviour learnt when training with regard for fairness: All lanes travel at roughly the same speeds.
![fair](https://raw.githubusercontent.com/nsidn98/MixedAutonomyRL/main/figures/fair2.png?token=AGFGCMAOELXU22OQX36XNVTAWKDVY)

## Variation in human-driver models:
We randomly created five different types of human drivers to add to the bottleneck environments. We change parameters like maximum-acceleration, driver pushiness, minimum desired following headway, speed gain, speed gain lookahead, impatience and cooperativeness. 

We found that adding a variety of human drivers to the environment during training and evaluation had little significant impact when compared to RL policies learned with less human driver variation during training and evaluation. These results held both with and without considering fairness (refer [report](https://github.com/nsidn98/MixedAutonomyRL/blob/main/MA_fairness.pdf) for more details).

## Acknowledgements:
We would like to thank the [6.884 Computational Sensorimotor Learning Spring 2021](https://pulkitag.github.io/6.884/) course staff for helpful discussions and their comments on our project scope and progress. We would also like to thank [Prof. Cathy Wu](http://www.wucathy.com/blog/) for helping us determine our project direction, and [Zhongxia Yan](https://github.com/ZhongxiaYan) for helping us get started with Flow. 

## Disclaimer:
Most of the results are preliminary and require more rigorous experiments to validate our hypothesis. For example: no hyperparameter tuning was carried out for optimising the models, training of the agents was carried out for a very low number of iterations due to compute and time (project deadline) constraints.
