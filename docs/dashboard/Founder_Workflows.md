# Founder Workflows

## Content approval

Draft creation → Guardian review → Founder inbox → source and version review → explicit Founder decision → server-side approval record → workflow continuation. A stale object version must return a conflict; the UI reloads instead of approving an old version.

`REQUEST_REVISION` preserves the original, stores the comment, creates a revision request, and returns the workflow to Content. `REJECT` stores the reason and blocks publication.

## Controls

Agent pause, global pause, publishing pause, and emergency stop always display confirmation. The API validates OWNER authority and records the result. Emergency stop preserves internal state, stops new external execution, pauses scheduling, and creates an incident. Clearing it follows the same controlled path.
