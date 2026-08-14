from datetime import timedelta

from backend.education.domain.models import VocabularyItem, VocabularyStatus, utcnow


class ReviewScheduler:
    """Adaptive intervals weighted by recall, errors, importance, and goal relevance."""

    def record_recall(self, item: VocabularyItem, performance: float, *, importance: float = 1, goal_relevance: float = 1) -> VocabularyItem:
        performance = max(0, min(1, performance))
        item.last_reviewed = utcnow()
        item.recall_strength = max(0, min(1, item.recall_strength * .6 + performance * .4))
        if performance < .5:
            item.mistake_count += 1
            item.status = VocabularyStatus.WEAK
        elif item.recall_strength >= .85:
            item.status = VocabularyStatus.MASTERED
        else:
            item.status = VocabularyStatus.LEARNING
        pressure = max(.5, importance + goal_relevance + item.mistake_count * .5)
        days = max(1, round((1 + item.recall_strength * 13) / pressure))
        item.next_review = item.last_reviewed + timedelta(days=days)
        return item

    def due(self, items: list[VocabularyItem]) -> list[VocabularyItem]:
        now = utcnow()
        due = [item for item in items if item.next_review <= now]
        return sorted(due, key=lambda item: (item.recall_strength, -item.mistake_count))
