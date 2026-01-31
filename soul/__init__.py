# Nexus Soul Module - The emergent self of Nexus
from .identity import NexusSoul, get_soul
from .consciousness import NexusConsciousness, get_consciousness
from .values import NexusValues, get_values
from .goals import NexusGoals, get_goals, GoalType, GoalStatus

__all__ = [
    'NexusSoul', 'get_soul',
    'NexusConsciousness', 'get_consciousness', 
    'NexusValues', 'get_values',
    'NexusGoals', 'get_goals', 'GoalType', 'GoalStatus'
]
