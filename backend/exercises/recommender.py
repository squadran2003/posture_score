from django.db.models import Avg

from posture.models import PostureScore, PostureSession

from .models import Exercise

# Maps scoring components to Exercise.target_issue values
COMPONENT_TO_TARGET = {
    "head_position_score": "forward_head",
    "shoulder_levelness_score": "shoulder_level",
    "shoulder_rounding_score": "shoulder_round",
    "spine_alignment_score": "spine_align",
}

# Threshold: component scores below this are considered weak
WEAK_THRESHOLD = 70


def get_weak_components(user, max_sessions=5):
    """
    Analyze the user's recent sessions and return a list of
    (component_field, avg_score) tuples sorted weakest-first.
    """
    recent_sessions = (
        PostureSession.objects.filter(user=user, is_active=False)
        .order_by("-started_at")[:max_sessions]
        .values_list("id", flat=True)
    )

    if not recent_sessions:
        return []

    avgs = PostureScore.objects.filter(session_id__in=list(recent_sessions)).aggregate(
        head_position_score=Avg("head_position_score"),
        shoulder_levelness_score=Avg("shoulder_levelness_score"),
        shoulder_rounding_score=Avg("shoulder_rounding_score"),
        spine_alignment_score=Avg("spine_alignment_score"),
    )

    weak = []
    for component, avg in avgs.items():
        if avg is not None and avg < WEAK_THRESHOLD:
            weak.append((component, avg))

    # Sort by score ascending (weakest first)
    weak.sort(key=lambda x: x[1])
    return weak


def recommend_exercises(user, limit=6):
    """
    Return a queryset of exercises targeted at the user's weakest posture
    components. Falls back to general exercises if no weak areas detected.
    """
    weak = get_weak_components(user)

    if not weak:
        # No data or everything is fine — return general exercises
        return Exercise.objects.filter(
            target_issue="general", is_premium=False
        ).order_by("difficulty", "name")[:limit]

    # Collect target issues from weak components, ordered by severity
    target_issues = []
    for component, _ in weak:
        target = COMPONENT_TO_TARGET.get(component)
        if target and target not in target_issues:
            target_issues.append(target)

    # Allocate exercise slots proportionally: more for weaker components
    # At minimum 1 per weak area, rest go to the weakest
    exercises = []
    seen_ids = set()
    per_issue = max(1, limit // len(target_issues))

    for target in target_issues:
        qs = (
            Exercise.objects.filter(target_issue=target, is_premium=False)
            .exclude(id__in=seen_ids)
            .order_by("difficulty", "name")[:per_issue]
        )
        for ex in qs:
            if len(exercises) >= limit:
                break
            exercises.append(ex)
            seen_ids.add(ex.id)

    # If we still have room, pad with general exercises
    if len(exercises) < limit:
        remaining = limit - len(exercises)
        general = (
            Exercise.objects.filter(target_issue="general", is_premium=False)
            .exclude(id__in=seen_ids)
            .order_by("difficulty", "name")[:remaining]
        )
        exercises.extend(general)

    return exercises
