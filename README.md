# Hyper-Dense-5G-Deployment-Problem

Optimization based approach for the Hyper-Dense 5G Network Deployment Problem.

## Problem definition

Given a set of users distributed over an area of interest, the objective is to find an optimized 5G network deployment design that minimizes cost and interferences while maximizing the coverage ratio, thus being a multi-objective optimization problem. The mathematical model used to represent the problem is based on the one proposed in _Shih-Jui Liu and Chun-Wei Tsai. An effective search algorithm for hyper-dense deployment problem of 5G. Procedia Computer Science 141:151–158, 01/2018_. Please, refer to this paper for further details.

## Software

According to their functionalities, the provided software can be logically splitted in several modules.

### Algorithms

Includes the implementation of the following optimization algorithms: several variations of [Simulated Annealing](src/algorithms/simulatedAnnealing.py), [Local Search](src/algorithms/localSearch.py) and several variations of [Adaptive Large Neighborhod Search](src/algorithms/ALNS.py).

Along with the algorithms, four [movement operators](src/algorithms/operators.py) are also provided. These can be passed on to the algorithms as a parameters, thus increasing flexibility.

### Representation

Data structures to store the information related to [instances](src/instance.py) and [deployments](src/deployment.py) is provided, along with methods to manipulate them.

### Instance generation

In order to produce synthetic instances for testing, an [instance generator](src/instanceGenerator.py) is included.

Two main kinds of instances can be generated: uniform and clusterized. The former uniformly distributes the users over the area of interest, while the latter makes custom clusters. Additionally, random compatibility restrictions between cells and candidate locations can also be defined.

When generating an instance, a file specifying the cells to be used should be passed on to the generator.

### KML parsing

Realistic instances can be loaded from KML files using the [parser](src/kmlParser.py) through the [instance](src/instance.py) class.

KML files must follow a specific format: the area of interest should be defined as a polygon named _P_, in whose description there should be an integer representing the number of users to be distributed over the area. Candidate installation locations are defined using placemarks named _CP_. In their description, a list of integers separated by spaces must be included. Every integer in the list should be the identifier for a cell compatible with the location.

### Visualization

A [tool for visualization](src/visualizer.py) is provided. It can plot both instances alone or both an instance and a corresponding deployment.

## Data

Together with the software, some data is also included to be used by other developers. Precisely, 16 [uniform instances](data/uniform/), eight with compatibility restrictions and eight without. 16 [clusterized instances](data/blobs/) in the same proportions. Three [KML instances](data/kml/). Additionally, some examples of [cell definition files](data/cells_default.txt) are also provided.

In the [results](results/) folder, results for some experiments using the algorithms over the uniform datasets are provided.
