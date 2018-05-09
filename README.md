[![Build Status](https://travis-ci.org/ACI-ESP/dworp.svg)](https://travis-ci.org/ACI-ESP/dworp)
[![Coverage Status](https://img.shields.io/coveralls/github/ACI-ESP/dworp.svg)](https://coveralls.io/github/ACI-ESP/dworp)

Dworp
=============
Flexible framework for building agent-based modeling simulations.

Requirements
--------------
 * python 3

Installation
--------------
Install using pip (maybe be pip3 on some platforms):
```
pip install dworp
```

To install with the optional plotting capability:
```
pip install dworp[plot]
```

Using
---------------
Dworp defines basic interfaces for building simulations and provides some
default components to support rapid creation of agent-based models.

### Agent
An agent updates its state in the `step()` function.
The update may depend on the environment, its neighbors, past history, or other features.

An agent has two optional functions `init()` and `complete()`.
The `init()` function is called when an agent is added to the simulation.
The `complete()` function is called at the end of a time step.

```python
class MyAgent(dworp.Agent):
    def step(self, new_time, env):
        # ToDo add example here
        pass
```

#### Visibility of Agent State
When agents are updating their state based on their neighbors' state, 
you may want to use a two stage update mechanism.
In the first stage, the agents update their state privately so that their neighbors
cannot see the new state.
In the second stage, the agents make that state public to prepare for the next time step.

### Environment
The environment captures all simulation state that does not live in the agents.
This includes serving as a container for network or spatial information for determining neighbors.

### Time
Time drives the simulation and implements an iterator interface.
Time can be fixed in length or infinite.
Time steps can be fixed in length or variable.
Time can be integer or floating point.

### Space
Agents can observe or interact with other agents based on neighborhoods.
A neighborhood may be defined on a network using various graph frameworks like igraph or snap.
A neighborhood can also be spatially defined on a grid or continuous space.

### Terminator
To stop the simulation when some condition is met, use a `Terminator`.

### Schedule
The order that agents update and which agents update is determined by the `Scheduler`.
Some basic schedulers are provided for round robin updates in random order or uniformly sampling.

### Observer
An `Observer` runs after each time step.
It is designed for capturing data for further processing.
It has access to the agents and the environment.
Multiple observers can be chained together using `ChainedObserver`.

### Simulation
The `Simulation` interface defines a single realization of an agent-based simulation.
Basic implementations for single stage and double stage updates are provided.
Usually, you will want to inherit from one of those to define your simulation.

### Logging
Each component has its own logger:
```python
    self.logger.info("Agent {} set activity to {}".format(self.agent_id, self.activity))
```
The logging level can be controlled at the framework level:
```python
    logging.getLogger('dworp').setLevel(logging.WARN)
```
or at the individual component level:
```python
    logging.getLogger('dworp.agent').setLevel(logging.DEBUG)
```

Examples
------------
The best way to learn the framework is by looking at the example models and their documentation.

Testing
-------------
To run the tests, use pip to install nose (pip install nose) and then in the base directory run:

```bash
nosetests
```

To get a report on unit test coverage:
```bash
nosetests --with-coverage --cover-package=dworp
```

Development
-----------
To install in editable model so that changes to the framework are instantly reflected:
```
pip install -e .
```

The code mostly follows the [PEP8 coding standard](https://www.python.org/dev/peps/pep-0008/).
If you are using PyCharm, it will highlight PEP8 issues.
You can also manually run style checks with flake8 (pip install flake8):
```bash
flake8 dworp
```

The docstrings are using the [Google standard](http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html).
