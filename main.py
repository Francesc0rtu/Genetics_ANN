from src.nn_encoding import *
from scripts.train import train, eval
from scripts.dataloader import MNIST, cifar10
from src.evolution import evolution
from torchsummary import summary

import csv
import sys
import imageio
from os import listdir
import time

from plot_results import plot_results

def run_evolution(dataset, population_size = 2, num_generations=2, batch_size=4, subpath =''):
    '''
    input: 
        - the dataset we want to train the population on
        - population_size: how many individuals for each generation
        - the number of generations we want to train
        - the batch_size associated to trainloader and testloader
        - subpath: the path where we want to save the results
    '''
    # create a population of random networks
    curr_env = evolution(population_size, holdout=0.6, mating=True, dataset=dataset, batch_size=batch_size)
    
    # run evolution and write result on file
    path = 'results/'
    if subpath:
        path += subpath 
        if not os.path.isdir(path):
            os.mkdir(path)
     
    f = open(f'{path}/all_generations_data.csv', 'w+', newline='')
    # create the csv writer
    writer = csv.writer(f)

    fieldnames = ['generation', 'individual', 'accuracy', 'num_layers', 'best_accuracy', 'best_num_layers']
    writer.writerow(fieldnames)
    res = []

    generations = num_generations
    for i in range(generations):
        gen = curr_env.generation()
        this_generation_best, best_score = curr_env.get_best_organism()
        best_net = this_generation_best
        print("Generation ", i , "'s best network accuracy: ", best_score, "%")
        for j in range(population_size):
            res.append([i, j, gen[j]['score'], gen[j]['len'], best_score, len(best_net)])

    # test last generation best organism
    trainloader , testloader, _, _, _ = dataset(batch_size)
    model = train(Net(best_net), trainloader , batch_size, all=True)
    acc = eval(model, testloader)

    original_stdout = sys.stdout # Save a reference to the original standard output
    with open('best_organism', 'w+') as d:
        sys.stdout = d
        print("Best organism accuracy: ", acc, "%")
        best_net.print_dsge_level()
        sys.stdout = original_stdout

    
    print("Best accuracy obtained: ", best_score)
    writer.writerows(res)
    f.close() 



def print_usage():
    print("Usage: python main.py [dataset] [population_size] [num_generations] [batch_size]")
    # add more info about which datasets are available
    sys.exit(1)

if __name__ == "__main__":
   
    # read arguments provided by user
    args = len(sys.argv) 

    # provide them all, otherwise they are set to default
    if args > 4: 
        if not isinstance(sys.argv[1], str) or not sys.argv[2].isdigit() or not sys.argv[3].isdigit() or not sys.argv[4].isdigit():  
            print_usage()
        else:
            # choose dataset
            if str(sys.argv[1]).lower() == 'cifar10':
                dataset = cifar10
            elif str(sys.argv[1]).lower() == 'mnist':
                dataset = MNIST
            else: 
                print_usage()
            
            # set population size
            population_size = int(sys.argv[2])
            # set number of generations
            num_generations = int(sys.argv[3])
            # set batch size
            batch_size = int(sys.argv[4])

    # set default values
    else: 
        dataset = MNIST
        population_size = 2
        num_generations = 2
        batch_size = 4

    

    # run evolution
    print("\n\n Evolution of a population of networks: \n\n")
    run_evolution(dataset, population_size, num_generations, batch_size, subpath = 'prova')

    #plot_results(population_size)

    