from src.ga_level import *


###########################
#   GA level  MUTATION    #
###########################


class ga_mutation_type(Enum):
    ADDITION = 0
    REPLACE = 1
    REMOVAL = 2

def choose_cut(netcode):
    "choose a random cut"
    cut = np.random.randint(0, netcode._len()-1)
    #identify the type of the cut
    cut_type = netcode.GA_encoding(cut).M_type

    #control we have not reached the maximum number of layers per module
    if cut_type == module_types.FEATURES and netcode.len_features() > MAX_LEN_FEATURES:
        if netcode.len_classification() < MAX_LEN_CLASSIFICATION:
            cut = np.random.randint(netcode.len_features(), netcode._len()-1) # if the max number of features is reached, the cut is chosen on classification module
        else:
            cut = None
    elif cut_type == module_types.CLASSIFICATION and netcode.len_classification() > MAX_LEN_CLASSIFICATION:
        if netcode.len_features() < MAX_LEN_FEATURES:
            cut = np.random.randint(0, netcode.len_features())
        else:
            cut = None

    return cut

def GA_mutation(offspring, type=None):
    "randomly choose the mutation type"
    if type == None:
        type = np.random.choice(list(ga_mutation_type))
    print("GA mutation type ", type)
    
    if type == ga_mutation_type.ADDITION:
        cut = choose_cut(offspring)
        if cut is not None:
            c_in =  np.random.randint(7,30) 
            c_out =  np.random.randint(7,30)
            cut_type = offspring.GA_encoding(cut).M_type
            if cut_type == module_types.FEATURES:
                module = Module(module_types.FEATURES,  c_out = c_out)
            elif cut_type == module_types.CLASSIFICATION:
                module = Module(module_types.CLASSIFICATION,  c_out = c_out)

            GA_add(offspring, cut, module)
        else:
            return offspring
    elif type == ga_mutation_type.REPLACE:
        GA_replace(offspring)
    else:
        GA_remove(offspring)


def GA_add(offspring, cut, module):

    # add control to check if we have reached the maximum number of modules
    # only features and classification modules can be added (replaced)
    if module.M_type == module_types.FEATURES:
        tmp = copy.deepcopy(offspring.features[cut:])
        offspring.features = copy.deepcopy(offspring.features[:cut + 1])

        # add the module
        offspring.features[cut] = copy.deepcopy(module)
        offspring.features.extend(tmp) # add the rest of the modules

    elif module.M_type == module_types.CLASSIFICATION:
        tmp = copy.deepcopy( offspring.classification[cut - offspring.len_features():]  )
        offspring.classification = copy.deepcopy(offspring.classification[:cut - offspring.len_features() + 1])
        
        # add the module
        offspring.classification[cut- offspring.len_features()] = copy.deepcopy(module)
        offspring.classification.extend(tmp) # add the rest of the modules
             

  

    

def GA_replace(offspring):
    "replace a module at random position"
    #find the position of the layer we want to copy
    cut1 = choose_cut(offspring) # choose_cut function controls we have not reached the limit of layers per module
    
    if cut1 is not None:
        #identify the type of the cut
        cut_type = offspring.GA_encoding(cut1).M_type

        # now find where we want to relocate (add) it
        if cut_type == module_types.FEATURES:
            cut2 = np.random.randint(0, offspring.len_features())
        elif cut_type == module_types.CLASSIFICATION:
            cut2 = np.random.randint(offspring.len_features(), offspring._len()-1)
        
        # The copy must be done by reference
        module = copy.deepcopy(offspring.GA_encoding(cut1)) # determine the module to copy
        GA_add(offspring, cut2, module)


 


def GA_remove(offspring):
    "remove a module at random position"
    #find cutting point
    cut = np.random.randint(0, offspring._len()-1)
    
    #identify the type of the cut
    cut_type = offspring.GA_encoding(cut).M_type

    if cut_type == module_types.FEATURES and offspring.len_features() <= 1: # if cut is of type features and there is only one module, we cannot remove it and we change it
        if offspring.len_classification() > 1:
            cut = np.random.randint(offspring.len_features(), offspring._len()-1) 
        else:
            cut = None
    elif cut_type == module_types.CLASSIFICATION and offspring.len_classification() <= 1: # if cut is of type classification and there is only one module, we cannot remove it and we change it
        if offspring.len_features() > 1: 
            cut = np.random.randint(0, offspring.len_features())
        else:
            cut = None

    if cut is not None:
        #identify the type of the cut which could have changed after the controls
        cut_type = offspring.GA_encoding(cut).M_type

        if cut_type == module_types.FEATURES:
            #remove the module
            offspring.features.pop(cut)

        elif cut_type == module_types.CLASSIFICATION:
            #remove the module
            offspring.classification.pop(cut - offspring.len_features())

    

    


       
###############################
#   DSGE level  MUTATION      #
###############################

"""
In DENSER we have three types of mutation at the dsge level:

* grammatical mutation: an expansion possibility is replaced by another one
* integer mutation: an integer block is replaced by another one
* float mutation: instead of randomly generating new values, a gaussian perturbation is applied 

"""

class dsge_mutation_type(Enum):
    GRAMMATICAL = 0
    INTEGER = 1

def dsge_mutation(offspring, type = None):
    "Mutation of the DSGE encoding."
    if type is None:
        type = np.random.choice(list(dsge_mutation_type))
        
    if type == dsge_mutation_type.GRAMMATICAL:
        grammatical_mutation(offspring)
    elif type == dsge_mutation_type.INTEGER:
        integer_mutation(offspring)

 

def grammatical_mutation(offspring):
    "Grammatical mutation of the DSGE encoding."
    
    #randomly choose a random gene
    gene = np.random.randint(0, offspring._len())
     
    #identify the gene
    gene_type = offspring.GA_encoding(gene).M_type
    
    print("grammatical mutation", gene_type)

    if gene_type == module_types.FEATURES:
        #choose a layer inside the gene
        layer = np.random.randint(0, offspring.features[gene].len())
        #identify the layer
        type = offspring.features[gene].layers[layer].type # this if you want to let unchanged the type of the layer
        #build a new layer mantaining the same type and the number of channels
        new_layer = Layer(type,  c_out = offspring.features[gene].layers[layer].channels['out'])  
        # add the new layer
        offspring.features[gene].layers[layer] = new_layer
        

    elif gene_type == module_types.CLASSIFICATION:
        #choose a layer inside the gene
        layer = np.random.randint(0, offspring.classification[gene - offspring.len_features()].len())
        #identify the layer
        type = offspring.classification[gene - offspring.len_features()].layers[layer].type
        #build a new layer mantaining the same type and the number of channels
        new_layer = Layer(type, c_out = offspring.classification[gene - offspring.len_features()].layers[layer].channels['out'])
        # add the new layer
        offspring.classification[gene - offspring.len_features()].layers[layer] = new_layer

    else:
        #choose a layer inside the gene
        layer = np.random.randint(0, offspring.last_layer[0].len())
        #identify the layer
        type = offspring.last_layer[0].layers[layer].type
        #build a new layer mantaining the same type and the number of channels
        new_layer = Layer(type,  c_out = offspring.last_layer[0].layers[layer].channels['out'])

        # add the new layer
        offspring.last_layer[0].layers[layer] = new_layer

    offspring.fix_first_classification()

    

def integer_mutation(offspring):
    "Integer mutation of the DSGE encoding."
    
    #randomly choose a random gene
    gene = np.random.randint(0, offspring._len())
    
    #identify the gene
    gene_type = offspring.GA_encoding(gene).M_type
    
    #change expansion rules within the gene by creating a new module
    new_module = Module(gene_type, c_out = offspring.GA_encoding(gene).param['output_channels'])

    print("integer mutation", gene_type)
    #replace new gene
    if gene_type == module_types.FEATURES:
        offspring.features[gene] = new_module

    elif gene_type == module_types.CLASSIFICATION:
        offspring.classification[gene - offspring.len_features()] = new_module
    else:
        offspring.last_layer[0] = new_module

    offspring.fix_first_classification()

    


