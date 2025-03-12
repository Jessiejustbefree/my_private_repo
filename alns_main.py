import os
import argparse
import numpy as np
import numpy.random as rnd
from operators import destroy_1, repair_1
from psp import PSP, Parser
from src.alns import ALNS
from src.alns.criteria import *
from src.helper import save_output
from src.settings import DATA_PATH


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='load data')
    parser.add_argument(dest='data', type=str, help='data')
    parser.add_argument(dest='seed', type=int, help='seed')
    args = parser.parse_args()
    
    # instance file and random seed
    json_file = args.data
    seed = int(args.seed)
    
    # instance file and random seed
    # json_file = "C:/Users/Jessie/OneDrive/桌面/Planning Decision Making/Assignment/code/psp_instances/sample_instances/S2.json"
    # seed = 606  

    # load data and random seed
    parsed = Parser(json_file)
    psp = PSP(parsed.name, parsed.workers, parsed.tasks, parsed.Alpha)

    # construct random initialized solution
    psp.random_initialize(seed)
    print("Initial solution objective is {}.".format(psp.objective()))

    # Generate output file
    save_output("LIU BINGCAN_ALNS", psp, "initial")  # // Modify with your name
    # print("初始解结束！")

    # ALNS
    random_state = rnd.RandomState(seed)
    alns = ALNS(random_state)
    # -----------------------------------------------------------------
    # // Implement Code Here
    # You should add all your destroy and repair operators here
    # add destroy operators
    alns.add_destroy_operator(destroy_1)
    # // add repair operators
    alns.add_repair_operator(repair_1)

    ## -----------------------------------------------------------------
    # ###标准1： hill climbing只接受更优解
    initial_solution=psp
    weights = [4, 2, 1, 0]

    result = alns.iterate(
    initial_solution,
    operator_decay=0.9,  
    criterion=HillClimbing(),  
    iterations=10000,
    weights=weights)
    ## result
    solution = result.best_state
    objective = solution.objective()
    print("没有regret版本 S2 爬山0.9 10000次 Best heuristic objective is {}.".format(objective))

##标准2 ：模拟退火
    ##Define Simulated Annealing parameters
    # accept = SimulatedAnnealing(
    #     start_temperature=5000,  # Starting temperature
    #     end_temperature=5,       # Ending temperature
    #     step=1-1e-4,           # Step size for temperature decay
    #     method="linear")     # Exponential cooling method

    # # # Weights for the ALNS algorithm
    # weights = [5, 2, 1, 0]  # Example weights, you should adjust these based on your problem

    # # Operator decay rate (this could be adjusted based on your ALNS design)
    # operator_decay=0.9

    # # Criterion: You may define a suitable criterion here; for simplicity, let's use SimulatedAnnealing
    # criterion=accept  # Or you can replace it with another criterion if necessary

    # # Run ALNS with Simulated Annealing acceptance
    # result=alns.iterate(psp, weights=weights, operator_decay=operator_decay, criterion=criterion, iterations=1000)

    # # result
    # solution = result.best_state
    # objective = solution.objective()
    # print("S1 模拟退火5000-5 0.9 1000 Best heuristic objective is {}.".format(objective))

    # visualize final solution and generate output file
    save_output("LIU BINGCAN_ALNS", solution, "solution")  # // Modify with your name

