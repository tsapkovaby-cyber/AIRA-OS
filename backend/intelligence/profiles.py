from .domain import Capability as C, RoutingPolicy as R, TaskProfile


DEFAULT_TASK_PROFILES = (
    TaskProfile("research_analysis", frozenset({C.LONG_CONTEXT, C.STRUCTURED_OUTPUT, C.REASONING}), policy=R.QUALITY_FIRST),
    TaskProfile("content_generation", frozenset({C.TEXT_GENERATION, C.MULTILINGUAL}), policy=R.QUALITY_FIRST),
    TaskProfile("guardian_review", frozenset({C.REASONING, C.STRUCTURED_OUTPUT}), minimum_reliability=.9, policy=R.CRITICAL_REVIEW),
    TaskProfile("founder_conversation", frozenset({C.FAST_RESPONSE, C.REASONING, C.MULTILINGUAL})),
    TaskProfile("knowledge_extraction", frozenset({C.STRUCTURED_OUTPUT}), minimum_reliability=.8),
    TaskProfile("planning", frozenset({C.REASONING, C.STRUCTURED_OUTPUT, C.LONG_CONTEXT}), policy=R.QUALITY_FIRST),
    TaskProfile("decision_support", frozenset({C.REASONING, C.STRUCTURED_OUTPUT})),
    TaskProfile("summarization", frozenset({C.TEXT_GENERATION})),
    TaskProfile("classification", frozenset({C.STRUCTURED_OUTPUT, C.FAST_RESPONSE, C.LOW_COST}), policy=R.LOW_COST),
    TaskProfile("coding_assistance", frozenset({C.CODE, C.REASONING})),
)

