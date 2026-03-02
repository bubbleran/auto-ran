#!/usr/bin/env python3
from bat.logging import create_logger
from langchain_core.tools import tool
from random import randint

logger = create_logger(__name__, "debug")

# Note: this file contains a dummy optimization tool which proposes an
#       increase of 20/24 dBm in the P0 Nominal. The choice is random.
#       You should replace the code of this function with a real
#       optimization algorithm.

@tool("optimize_p0")
def optimize_p0_tool(
    ul_throughput_current: float, # not used
    p0_current: int,
) -> int:
    """
    Use an optimization algorithm to propose an optimized P0 Nominal value for the network,
    based on current P0 Nominal and current Uplink Throughput.

    Params:
        - ul_throughput_current(float): current Uplink Throughput in Mbps.
        - p0_current(int): current P0 Nominal in dBm.

    Returns:
        int: the new P0 Nominal proposal
    """
    logger.debug(f"[optimize_p0_tool] ul_throughput_current: {ul_throughput_current}, p0_current: {p0_current}")
    deltas = [+20, +24]
    idx = randint(0, len(deltas))
    delta = deltas[idx]
    
    proposal = p0_current + delta
    
    logger.debug(f"[optimize_p0_tool] proposal: {proposal}")
    return proposal
