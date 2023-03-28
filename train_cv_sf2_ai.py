import gym
import cv2
import retro
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.preprocessing import is_image_space, is_image_space_channels_first
import torch
import torch.nn as nn

from custom_cnn import CustomCNN
from custom_sf2_cv_env import StreetFighterCustomWrapper

def make_env(game, state, seed=0):
    def _init():
        win_template = cv2.imread('images/pattern_wins_gray.png', cv2.IMREAD_GRAYSCALE)
        lose_template = cv2.imread('images/pattern_lose_gray.png', cv2.IMREAD_GRAYSCALE)
        env = retro.RetroEnv(game=game, state=state, obs_type=retro.Observations.IMAGE)
        env = StreetFighterCustomWrapper(env, win_template, lose_template)
        env.seed(seed)
        return env
    return _init

def main():
    # Set up the environment and model
    game = "StreetFighterIISpecialChampionEdition-Genesis"
    state_stages = [
        "Champion.Level1.ChunLiVsGuile",
        "Champion.Level2.ChunLiVsKen",
        "Champion.Level3.ChunLiVsChunLi",
        "Champion.Level4.ChunLiVsZangief",
        # Add other stages as necessary
    ]

    num_envs = 8

    env = SubprocVecEnv([make_env(game, state_stages[0], seed=i) for i in range(num_envs)])

    policy_kwargs = {
        'features_extractor_class': CustomCNN
    }

    model = PPO(
        "CnnPolicy", 
        env,
        device="cuda", 
        policy_kwargs=policy_kwargs, 
        verbose=1
    )
    model.learn(total_timesteps=int(1000))

    model.save("ppo_sf2_cnn")

if __name__ == "__main__":
    main()