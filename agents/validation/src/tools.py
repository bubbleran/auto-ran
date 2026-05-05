import os
from dotenv import load_dotenv
from bat.logging import create_logger
from langchain_core.tools import tool
from typing import Dict, Optional

load_dotenv()
logger = create_logger(__name__, "debug")

# Default P0 nominal of the network
WELL_KNOWN_P0 = int(os.getenv("WELL_KNOWN_P0", -100))
# UL throughput in the DT with the default P0 nominal
WELL_KNOWN_UL = float(os.getenv("WELL_KNOWN_UL", 160000.0))

p0_cache: Dict[int, float] = { WELL_KNOWN_P0: WELL_KNOWN_UL }

@tool(name_or_callable="read_from_memory")
def read_from_memory(
    p0_nominal: int,
) -> Optional[float]:
    """
    Read the measured Uplink Throughput for the specified P0 Nominal.
    
    Params:
        - p0_nominal(int): value of the P0 Nominal for which you want to know the measured throughput.
    
    Result:
        Optional[float]: the measured throughput for the specified P0 Nominal in kbps, or None if not available
    """
    global p0_cache
    return p0_cache.get(p0_nominal)

@tool(name_or_callable="write_to_memory")
def write_to_memory(
    p0_nominal: int,
    ul_throuhgput: float,
) -> bool:
    """
    Save the measured Uplink Throughput for the specified P0 Nominal.
    
    Params:
        - p0_nominal(int): value of the new P0 Nominal for which you want to save the measured throughput.
        - ul_throughput(float): value of the measured throughput to write (in kbps)
    
    Result:
        bool: result of the operation (True if success, False otherwise).
    """
    global p0_cache
    p0_cache[p0_nominal] = ul_throuhgput
    return True
