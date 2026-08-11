# Identity Evaluation

The evaluator is a port designed to combine face-embedding similarity, visual feature checks, Founder ratings, experiments and manual Guardian review; an LLM similarity statement alone is insufficient. Identity and quality scores remain separate. Suggested bands are 90–100 excellent, 80–89 acceptable, 70–79 review, and below 70 reject. Founder rejection is final even at 93.

Quality adapters should check hands/fingers, anatomy, asymmetric eyes, teeth, jewelry, text, objects, reflections and duplication. Feedback records target, category, severity, reason, Founder and timestamp; it informs prompts, selection and experiments but never triggers blind retraining.
