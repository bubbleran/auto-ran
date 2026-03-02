**Config Planner Agent**
Plans and enforces p0-nominal changes by combining monitoring KPIs, optimization inference, and digital-twin validation. Designed for A2A topologies (supervised or custom).

**Workflow**
1. Call Monitoring Agent (A2A) to fetch KPIs.
2. Run optimization inference to propose a single recommended p0 value.
3. Call Validator Agent (A2A) to test that one value in the digital twin.
4. Decide the final p0-nominal and enforce via OAM.

**Environment**
- `NETWORK_ID`: Target network ID for p0 enforcement (default `bubbleran`).
- `ACCESS_INDEX`: Access index for p0 enforcement (default `0`).
- `MONITORING_AGENT_NAME`: A2A agent name for monitoring (default `monitoring-agent`).
- `VALIDATOR_AGENT_NAME`: A2A agent name for validation (default `validator-agent`).
