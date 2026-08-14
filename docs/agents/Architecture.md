# Architecture

`AgentManifest` is validated and registered against approved prompts and separately registered tools. Registration preserves version records but never auto-activates a candidate version. `AgentRuntime.execute` accepts only Workflow-assigned `AgentTask` objects, checks the global pause, registry status, Guardian decision, task/agent tool intersection, permission requirements, and timeout before provider routing.

Results conform to `AgentResult` and all lifecycle and execution actions append `AuditRecord` entries. Agents cannot invoke one another: results return to Workflow, which may emit shared events. `GlobalAgentControl` provides the Founder kill switch. The runtime supplies external content as data and builds a minimal context package.
