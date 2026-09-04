"""
OptiFlow - High-Performance Windows System Optimization & Flow Guardian
"""

__version__ = "1.0.0"
__author__ = "Devansh Ganatra"

from .optiflow_core import (
    get_memory_status,
    get_process_list,
    optimize_idle_memory,
    boost_dev_flow,
    clean_temp_cache,
    reap_zombies
)
from .optiflow_daemon import daemon_instance
