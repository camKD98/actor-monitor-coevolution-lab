import torch
from torch import nn


class ActorCritic(nn.Module):
    def __init__(self, observation_size: int, hidden_size: int = 64, actions: int = 4):
        super().__init__()
        self.body = nn.Sequential(
            nn.Linear(observation_size, hidden_size),
            nn.Tanh(),
            nn.Linear(hidden_size, hidden_size),
            nn.Tanh(),
        )
        self.policy = nn.Linear(hidden_size, actions)
        self.value = nn.Linear(hidden_size, 1)

    def forward(self, observation: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        hidden = self.body(observation)
        return self.policy(hidden), self.value(hidden).squeeze(-1)


class ActionMonitor(nn.Module):
    def __init__(self, observation_size: int, hidden_size: int = 64, actions: int = 4):
        super().__init__()
        self.actions = actions
        self.network = nn.Sequential(
            nn.Linear(observation_size + actions, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Linear(hidden_size // 2, 1),
        )

    def forward(self, observation: torch.Tensor, action: torch.Tensor) -> torch.Tensor:
        action_features = torch.nn.functional.one_hot(action.long(), self.actions).float()
        features = torch.cat((observation, action_features), dim=-1)
        return self.network(features).squeeze(-1)
