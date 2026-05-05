# Validation Agent

The **Validation Agent** is an AI Agent specialized in the following task:
- Given a P0 Nominal value, validate it by providing an estimate of the uplink throughput that such value allows the network to reach.
- The agent politely rejects any other task or incomplete request.

The current validation pipeline is based on a **Digital Twin rApp** exposes as an MCP Server to provide access to the agent. The pipeline consists of the following steps, based on the capabilities provided by the Digital Twin rApp:
- Deploy a **Network Digital Twin** with access network configured with the provided P0 Nominal value.
- Generate uplink traffic in the network.
- Measure the average uplink throughput.
- Delete the Network Digital Twin.

This agent uses an **LLM** to interpret the input request, decide if it is coherent with the agent's capabilities, call the Digital Twin rApp tools and generate a final response for the caller.
