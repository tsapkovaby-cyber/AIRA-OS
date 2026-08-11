# Cost Control

Profiles express input/output price per thousand tokens. Routing estimates request cost, while `BudgetLedger` authorizes before invocation and records accepted inference cost. The initial ledger enforces per-task/project ceilings; daily agent/provider and monthly persistence are extension points.

