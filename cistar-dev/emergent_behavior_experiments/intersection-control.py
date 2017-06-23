"""
Script used to train vehicles to stop crashing longitudinally and on intersections.
"""

import logging

from rllab.envs.normalized_env import normalize
from rllab.misc.instrument import stub, run_experiment_lite
from rllab.algos.trpo import TRPO
from rllab.baselines.linear_feature_baseline import LinearFeatureBaseline
from rllab.policies.gaussian_mlp_policy import GaussianMLPPolicy

# from cistar.core.exp import SumoExperiment
from cistar.envs.loop_accel import SimpleAccelerationEnvironment
from cistar.scenarios.loop.loop_scenario import LoopScenario
from cistar.scenarios.figure8.figure8_scenario import Figure8Scenario
from cistar.controllers.car_following_models import *
from cistar.controllers.rlcontroller import RLController
from cistar.controllers.lane_change_controllers import *

logging.basicConfig(level=logging.INFO)

stub(globals())

sumo_params = {"time_step": 0.1, "traci_control": 1, "rl_lc": "no_collide", "human_lc": "no_collide",
               "rl_sm": "no_collide", "human_sm": "no_collide"}
sumo_binary = "sumo"

env_params = {"target_velocity": 30, "max-deacc": -6, "max-acc": 3, "fail-safe": "None",
              "intersection_fail-safe": "None"}

net_params = {"radius_ring": 30, "lanes": 1, "speed_limit": 30, "resolution": 40,
              "net_path": "debug/net/"}

cfg_params = {"start_time": 0, "end_time": 30000, "cfg_path": "debug/rl/cfg/"}

initial_config = {"shuffle": False}

num_cars = 20
num_auto = 15

exp_tag = str(num_cars) + '-car-' + str(num_auto) + '-rl-intersection-control'

# type_params = {"rl": (1, (RLController, {}), (StaticLaneChanger, {}), 0),
#                "idm": (9, (IDMController, {}), (StaticLaneChanger, {}), 0),
#                "rl2": (1, (RLController, {}), (StaticLaneChanger, {}), 0),
#                "idm2": (9, (IDMController, {}), (StaticLaneChanger, {}), 0)}

# type_params = {"rl": (1, (RLController, {}), (StaticLaneChanger, {}), 0),
#                "idm": (4, (IDMController, {}), (StaticLaneChanger, {}), 0),
#                "rl2": (1, (RLController, {}), (StaticLaneChanger, {}), 0),
#                "idm2": (4, (IDMController, {}), (StaticLaneChanger, {}), 0),
#                "rl3": (1, (RLController, {}), (StaticLaneChanger, {}), 0),
#                "idm3": (4, (IDMController, {}), (StaticLaneChanger, {}), 0),
#                "rl4": (1, (RLController, {}), (StaticLaneChanger, {}), 0),
#                "idm4": (4, (IDMController, {}), (StaticLaneChanger, {}), 0)}

# type_params = {"rl": (1, (RLController, {}), (StaticLaneChanger, {}), 0),
#                "idm": (3, (IDMController, {}), (StaticLaneChanger, {}), 0),
#                "rl2": (1, (RLController, {}), (StaticLaneChanger, {}), 0),
#                "idm2": (3, (IDMController, {}), (StaticLaneChanger, {}), 0),
#                "rl3": (1, (RLController, {}), (StaticLaneChanger, {}), 0),
#                "idm3": (3, (IDMController, {}), (StaticLaneChanger, {}), 0),
#                "rl4": (1, (RLController, {}), (StaticLaneChanger, {}), 0),
#                "idm4": (3, (IDMController, {}), (StaticLaneChanger, {}), 0),
#                "rl5": (1, (RLController, {}), (StaticLaneChanger, {}), 0),
#                "idm5": (3, (IDMController, {}), (StaticLaneChanger, {}), 0)}

# type_params = {"rl": (1, (RLController, {}), (StaticLaneChanger, {}), 0),
#                "idm": (1, (IDMController, {}), (StaticLaneChanger, {}), 0),
#                "rl2": (1, (RLController, {}), (StaticLaneChanger, {}), 0),
#                "idm2": (1, (IDMController, {}), (StaticLaneChanger, {}), 0),
#                "rl3": (1, (RLController, {}), (StaticLaneChanger, {}), 0),
#                "idm3": (1, (IDMController, {}), (StaticLaneChanger, {}), 0),
#                "rl4": (1, (RLController, {}), (StaticLaneChanger, {}), 0),
#                "idm4": (1, (IDMController, {}), (StaticLaneChanger, {}), 0),
#                "rl5": (1, (RLController, {}), (StaticLaneChanger, {}), 0),
#                "idm5": (1, (IDMController, {}), (StaticLaneChanger, {}), 0),
#                "rl6": (1, (RLController, {}), (StaticLaneChanger, {}), 0),
#                "idm6": (1, (IDMController, {}), (StaticLaneChanger, {}), 0),
#                "rl7": (1, (RLController, {}), (StaticLaneChanger, {}), 0),
#                "idm7": (1, (IDMController, {}), (StaticLaneChanger, {}), 0),
#                "rl8": (1, (RLController, {}), (StaticLaneChanger, {}), 0),
#                "idm8": (1, (IDMController, {}), (StaticLaneChanger, {}), 0),
#                "rl9": (1, (RLController, {}), (StaticLaneChanger, {}), 0),
#                "idm9": (1, (IDMController, {}), (StaticLaneChanger, {}), 0),
#                "rl10": (1, (RLController, {}), (StaticLaneChanger, {}), 0),
#                "idm10": (1, (IDMController, {}), (StaticLaneChanger, {}), 0)}

type_params = {"rl": (3, (RLController, {}), (StaticLaneChanger, {}), 0),
               "idm": (1, (IDMController, {}), (StaticLaneChanger, {}), 0),
               "rl2": (3, (RLController, {}), (StaticLaneChanger, {}), 0),
               "idm2": (1, (IDMController, {}), (StaticLaneChanger, {}), 0),
               "rl3": (3, (RLController, {}), (StaticLaneChanger, {}), 0),
               "idm3": (1, (IDMController, {}), (StaticLaneChanger, {}), 0),
               "rl4": (3, (RLController, {}), (StaticLaneChanger, {}), 0),
               "idm4": (1, (IDMController, {}), (StaticLaneChanger, {}), 0),
               "rl5": (3, (RLController, {}), (StaticLaneChanger, {}), 0),
               "idm5": (1, (IDMController, {}), (StaticLaneChanger, {}), 0)}

# type_params = {"rl": (20, (RLController, {}), (StaticLaneChanger, {}), 0)}

scenario = Figure8Scenario(exp_tag, type_params, net_params, cfg_params, initial_config=initial_config)

env = SimpleAccelerationEnvironment(env_params, sumo_binary, sumo_params, scenario)

env = normalize(env)

for seed in [5]:  # [16, 20, 21, 22]:
    policy = GaussianMLPPolicy(
        env_spec=env.spec,
        hidden_sizes=(100, 50, 25)
    )

    baseline = LinearFeatureBaseline(env_spec=env.spec)

    algo = TRPO(
        env=env,
        policy=policy,
        baseline=baseline,
        batch_size=15000,
        max_path_length=1500,
        n_itr=1000,
        # whole_paths=True,
        discount=0.999,
        step_size=0.01,
    )

    run_experiment_lite(
        algo.train(),
        # Number of parallel workers for sampling
        n_parallel=8,
        # Only keep the snapshot parameters for the last iteration
        snapshot_mode="all",
        # Specifies the seed for the experiment. If this is not provided, a random seed
        # will be used
        seed=seed,
        mode="ec2",
        exp_prefix=exp_tag,
        # python_command="/home/aboudy/anaconda2/envs/rllab3/bin/python3.5"
        # plot=True,
    )
