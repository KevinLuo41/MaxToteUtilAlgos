# max_tote_util_algo

max_tote_util_algo is the package that improve the tote utilization in the fulfillment center. 
Two problems are trying to be solved - decanting and tote merge

## Folder Structure

```
max_tote_util_algo
└── MaxToteUtilAlgos
    ├── decanting
    │   ├── data
    │   ├── genetic
    │   │   └── result
    │   └── greedy
    │       └── result
    ├── tote_merge
    │   ├── data
    │   ├── result
    │   └── greedy
    ├── entities
    └── test
```
## How to Start
vpython and recpack are two uncommon packages that need to be install first.
Open max_tote_util_algo as a project. 

Execute main function of each algo to run experiments. 

## Entities
Entities includes the element classes that shared across different algorithms

## APIs


* class **GreedyPack**([, packs][, tote][, num_stations][, target_util][, NUM_PROCS][, brute][, rect])  
  Return a GeneticPack object.
  
  GreedyPack can be used as greedy packing or random brute force. Switch algo by change the 'brute' flag.
  
  * packs: a sequence of inbound cases
  * tote: a standard empty tote
  * num_stations: number of open decanting stations.
  * target_util: a utilization threshold above which the tote will be closed and pushed. 
  * NUM_PROCS: num of cpu processors are gonna used. Notice: using parallel computing does not necessarily save the run time when input size is small. 
  * brute: a flag if true this brute force algo will be excuted, o.w. greedy - . 
  * rect: a flag if true rectpack will be used for bin pack, o.w. Packman will be used. 
  * OTHER PARAMETERS: see wiki: genetic algorithm or the reference paper


* class **GeneticPack**([, packs][, tote][, tote_try][, stack][, NUM_PROCS][, POP_SIZE][, GENERATIONS][, MUTATION_RATE][, ELITE_CNT][, PROB_GOOD_PARENT][,PROB_INFERTILE_PARENTS])  
  Return a GeneticPack object
  
  * packs: a sequence of inbound cases
  * tote: a standard empty tote
  * tote_try: minimum number of tote, if none return a liquid volume minimum number of totes
  * stack: if different skus can be stacked together
  * NUM_PROCS: num of cpu processors are gonna used. Notice: using parallel computing does not necessarily save the run time when input size is small. 
  * OTHER PARAMETERS: see wiki: genetic algorithm or the reference paper
  
  
* class **ToteMerger**([, tote])  
  Return a GeneticPack object
 
  * totes: a list of totes to be merged
  * merger.merge_max_util: call max_util_merge, return list of merged totes
  * merger.merge_in_order: call in_order_merge, return none; call merger.result_merge to get the dict of merged totes. 

## TODO
* Break pack logic with rectpack package
* over/under pack implementation 

