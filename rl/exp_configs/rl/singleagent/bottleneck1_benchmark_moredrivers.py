"""Benchmark for bottleneck1.

Bottleneck in which the actions are specifying a desired velocity in a segment
of space. The autonomous penetration rate in this example is 25%.
Human lane changing is enabled.

- **Action Dimension**: (?, )
- **Observation Dimension**: (?, )
- **Horizon**: 1000 steps
"""
# from flow.envs import BottleneckDesiredVelocityEnv
import sys, os
sys.path.append(os.path.abspath(os.getcwd()))
from envs.bottleneck import BottleneckDesiredVelocityEnv
from flow.networks import BottleneckNetwork
from flow.core.params import SumoParams, EnvParams, InitialConfig, NetParams, \
    InFlows, SumoCarFollowingParams, SumoLaneChangeParams
from flow.core.params import TrafficLightParams
from flow.core.params import VehicleParams
from flow.controllers import RLController, ContinuousRouter

# time horizon of a single rollout
HORIZON = 1500

N_CPUS = 2
N_ROLLOUTS = N_CPUS * 4
SCALING = 1
NUM_LANES = 4 * SCALING  # number of lanes in the widest highway
DISABLE_TB = True
DISABLE_RAMP_METER = True
# AV_FRAC = 0.25
AV_FRAC = 0.1

vehicles = VehicleParams()

import numpy as np
import random
driver_params = [] # list of dictionaries of human driver params
num_humans = 5
sim_step_ = 0.5 # defined later in the file under flow_params
for i in range(num_humans):
    max_accel = np.random.normal(2.7, 0.1)
    tau = np.random.normal(1, 1)
    tau = max(sim_step_, tau)
    tau = min(tau, 4)
    speedgain = np.random.normal(1, 1)
    speedgain = max(0, speedgain)
    speedgain = min(speedgain, 2)
    speedgain_lookahead = np.random.poisson(1)
    speedgain_lookahead = max(5, speedgain_lookahead)
    pushy = 0.3
    impatience = np.random.normal(0, 0.16)
    impatience = max(0.5, impatience)
    impatience = min(impatience, -0.5)
    cooperative = np.random.uniform(0, 1)
    d = {'max_a': max_accel, 'tau': tau, 'speedgain': speedgain,
            'speedgain_lookahead': speedgain_lookahead,
            'pushy': pushy,
            'impatience': impatience,
            'cooperative': cooperative
    }
    driver_params.append(d)
for i in range(num_humans):
    p = driver_params[i]
    vehicles.add(
        veh_id='human_'+str(i),
        routing_controller=(ContinuousRouter, {}),
        car_following_params=SumoCarFollowingParams(
            speed_mode=9,
            accel=p['max_a'],
            tau = p['tau'],
        ),
        lane_change_params=SumoLaneChangeParams(
            lane_change_mode = 0, #"sumo_default",
            lc_speed_gain = p['speedgain'],
            lc_pushy = p['pushy'],
            lc_cooperative = p['cooperative'],
        ),
        num_vehicles = 1 * SCALING)

vehicles.add(
    veh_id="human",
    routing_controller=(ContinuousRouter, {}),
    car_following_params=SumoCarFollowingParams(
        speed_mode=9,
    ),
    lane_change_params=SumoLaneChangeParams(
        lane_change_mode=1621,
    ),
    num_vehicles=1 * SCALING)
vehicles.add(
    veh_id="rl",
    acceleration_controller=(RLController, {}),
    routing_controller=(ContinuousRouter, {}),
    car_following_params=SumoCarFollowingParams(
        speed_mode=9,
    ),
    lane_change_params=SumoLaneChangeParams(
        lane_change_mode=0,
    ),
    num_vehicles=1 * SCALING)

controlled_segments = [("1", 1, False), ("2", 2, True), ("3", 2, True),
                       ("4", 2, True), ("5", 1, False)]
num_observed_segments = [("1", 1), ("2", 3), ("3", 3), ("4", 3), ("5", 1)]
additional_env_params = {
    "target_velocity": 40,
    "disable_tb": True,
    "disable_ramp_metering": True,
    "controlled_segments": controlled_segments,
    "symmetric": False,
    "observed_segments": num_observed_segments,
    "reset_inflow": False,
    "lane_change_duration": 5,
    "max_accel": 3,
    "max_decel": 3,
    "inflow_range": [1200, 2500]
}

# flow rate
flow_rate = 2500 * SCALING

# percentage of flow coming out of each lane
inflow = InFlows()

for i in range(num_humans):
    inflow.add(
        veh_type='human_'+str(i),
        edge="1",
        vehs_per_hour= flow_rate * ((1 - AV_FRAC)/(num_humans + 1)),
        departLane = 'random',
        departSpeed=10
    )

inflow.add(
    veh_type="human",
    edge="1",
    vehs_per_hour=flow_rate * ((1 - AV_FRAC)/(num_humans+1)),
    departLane="random",
    departSpeed=10)
inflow.add(
    veh_type="rl",
    edge="1",
    vehs_per_hour=flow_rate * AV_FRAC,
    departLane="random",
    departSpeed=10)

traffic_lights = TrafficLightParams()
if not DISABLE_TB:
    traffic_lights.add(node_id="2")
if not DISABLE_RAMP_METER:
    traffic_lights.add(node_id="3")

additional_net_params = {"scaling": SCALING, "speed_limit": 23}
net_params = NetParams(
    inflows=inflow,
    additional_params=additional_net_params)

flow_params = dict(
    # name of the experiment
    exp_tag="bottleneck_1",

    # name of the flow environment the experiment is running on
    env_name=BottleneckDesiredVelocityEnv,

    # name of the network class the experiment is running on
    network=BottleneckNetwork,

    # simulator that is used by the experiment
    simulator='traci',

    # sumo-related parameters (see flow.core.params.SumoParams)
    sim=SumoParams(
        sim_step=0.5,
        render=False,
        print_warnings=False,
        restart_instance=True,
    ),

    # environment related parameters (see flow.core.params.EnvParams)
    env=EnvParams(
        warmup_steps=40,
        sims_per_step=1,
        horizon=HORIZON,
        additional_params=additional_env_params,
    ),

    # network-related parameters (see flow.core.params.NetParams and the
    # network's documentation or ADDITIONAL_NET_PARAMS component)
    net=NetParams(
        inflows=inflow,
        additional_params=additional_net_params,
    ),

    # vehicles to be placed in the network at the start of a rollout (see
    # flow.core.params.VehicleParams)
    veh=vehicles,

    # parameters specifying the positioning of vehicles upon initialization/
    # reset (see flow.core.params.InitialConfig)
    initial=InitialConfig(
        spacing="uniform",
        min_gap=5,
        lanes_distribution=float("inf"),
        edges_distribution=["2", "3", "4", "5"],
    ),

    # traffic lights to be introduced to specific nodes (see
    # flow.core.params.TrafficLightParams)
    tls=traffic_lights,
)
