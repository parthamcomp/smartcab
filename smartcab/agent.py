import random
import math
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator


class LearningAgent(Agent):
    """ An agent that learns to drive in the Smartcab world.
        This is the object you will be modifying. """

    def __init__(self, env, learning=False, epsilon=1.0, alpha=0.5):
        super(LearningAgent, self).__init__(env)  # Set the agent in the evironment
        self.planner = RoutePlanner(self.env, self)  # Create a route planner
        self.valid_actions = self.env.valid_actions  # The set of valid actions

        # Set parameters of the learning agent
        self.learning = learning  # Whether the agent is expected to learn
        self.Q = dict()  # Create a Q-table which will be a dictionary of tuples
        self.epsilon = epsilon  # Random exploration factor
        self.alpha = alpha  # Learning factor

        self.t = 0

    def reset(self, destination=None, testing=False):
        """ The reset function is called at the beginning of each trial.
            'testing' is set to True if testing trials are being used
            once training trials have completed. """

        # Select the destination as the new location to route to
        self.planner.route_to(destination)

        if testing:
            self.epsilon = 0
            self.alpha = 0
        else:
            self.t = self.t + 1
            self.epsilon = math.fabs(math.cos(self.alpha*self.t))
        return None

    def build_state(self):
        """ The build_state function is called when the agent requests data from the 
            environment. The next waypoint, the intersection inputs, and the deadline 
            are all features available to the agent. """

        # Collect data about the environment
        waypoint = self.planner.next_waypoint()  # The next waypoint
        inputs = self.env.sense(self)  # Visual input - intersection light and traffic
        deadline = self.env.get_deadline(self)  # Remaining deadline

        state = (waypoint, inputs['right'], inputs['left'], inputs['oncoming'])
        buildString = lambda s: None if s is None else str(s)
        state = [buildString(s) for s in state]

        return state

    def get_maxQ(self, state):
        """ The get_maxQ function is called when the agent is asked to find the
            maximum Q-value of all actions based on the 'state' the smartcab is in. """
        maxQ = float('-inf')
        for action in self.Q[state]:
            if maxQ < self.Q[state][action]:
                maxQ = self.Q[state][action]
        return maxQ

    def createQ(self, state):
        """ The createQ function is called when a state is generated by the agent. """

        if self.learning:
            self.Q[state] = self.Q.get(state, {None: 0.0, 'forward': 0.0, 'left': 0.0, 'right': 0.0})
        return

    def choose_action(self, state):
        """ The choose_action function is called when the agent is asked to choose
            which action to take, based on the 'state' the smartcab is in. """

        # Set the agent state and default action
        self.state = state
        self.next_waypoint = self.planner.next_waypoint()
        action = None

        # FAI5100 - Returning the best choice from the list of valid actions.
        comp = random.random
        if self.learning:
            if comp < self.epsilon:
                action = random.choice(self.valid_actions)
            else:
                valid_actions = []
                maxQ = self.get_maxQ(state)
                for a in self.Q[state]:
                    if maxQ == self.Q[state][a]:
                        valid_actions.append(a)
                action = random.choice(valid_actions)
        else:
            action = random.choice(self.valid_actions)
        return action

    def learn(self, state, action, reward):
        """ The learn function is called after the agent completes an action and
            receives a reward. This function does not consider future rewards 
            when conducting learning. """

        if self.learning:
            self.Q[state][action] = self.Q[state][action] + self.alpha * (reward - self.Q[state][action])
        return

    def update(self):
        """ The update function is called when a time step is completed in the 
            environment for a given trial. This function will build the agent
            state, choose an action, receive a reward, and learn if enabled. """

        state = self.build_state()  # Get current state
        self.createQ(state)  # Create 'state' in Q-table
        action = self.choose_action(state)  # Choose an action
        reward = self.env.act(self, action)  # Receive a reward
        self.learn(state, action, reward)  # Q-learn

        return


def run():
    """ Driving function for running the simulation. 
        Press ESC to close the simulation, or [SPACE] to pause the simulation. """

    ##############
    # Create the environment
    # Flags:
    #   verbose     - set to True to display additional output from the simulation
    #   num_dummies - discrete number of dummy agents in the environment, default is 100
    #   grid_size   - discrete number of intersections (columns, rows), default is (8, 6)
    env = Environment()

    ##############
    # Create the driving agent
    # Flags:
    #   learning   - set to True to force the driving agent to use Q-learning
    #    * epsilon - continuous value for the exploration factor, default is 1
    #    * alpha   - continuous value for the learning rate, default is 0.5
    agent = env.create_agent(LearningAgent)

    ##############
    # Follow the driving agent
    # Flags:

    # FAI5100 - Setting the enforce_deadline to force the agent to capture if it reaches destination on time.
    enforce_deadline = True
    env.set_primary_agent(agent)

    ##############
    # Create the simulation
    # Flags:
    # FAI5100 - Updated the time delay between each time step.
    update_delay = 0.01
    #   display      - set to False to disable the GUI if PyGame is enabled

    # FAI5100 - Set this to True to log the simulation results as a .csv file in /logs/.
    log_metrics = True

    #   optimized    - set to True to change the default log file name
    sim = Simulator(env)

    ##############
    # Run the simulator
    # Flags:
    #   tolerance  - epsilon tolerance before beginning testing, default is 0.05

    # FAI5100 - Set the n_test flag to run 10 testing trials.
    n_test = 10

    sim.run()


if __name__ == '__main__':
    run()
