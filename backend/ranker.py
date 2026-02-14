from datetime import datetime
from math import exp
from backend.feedback import get_feedback


def recency_score(dt):
    """
    Calculate a recency score based on the date.

    Args:
        dt (datetime): The datetime of the solution.

    Returns:
        float: Recency score between 0 and 1.
    """
    if not dt:
        return 0.0
    days = (datetime.utcnow() - dt).days
    return exp(-days / 180)


def rank_solutions(ticket):
    """
    Rank solutions for a ticket based on similarity, recency, and feedback.

    Args:
        ticket (dict): The support ticket dictionary.
        similarity (float): Similarity score of the ticket to the query.
    
    Returns:
        list: Ranked list of solutions with their scores.
    """
    ranked = []

    for sol in ticket["solutions"]:
        feedback_score = get_feedback(ticket["ticket_id"], sol["level"])
        recency = recency_score(sol["date"])  # In case solution dates are proposed at independent times
        escalation_penalty = 0.1 * (sol["level"] - 1)

        # These parameters can be tuned as needed
        final_score = (
            0.7 * feedback_score -   # Feedback score has most weight
            escalation_penalty       # Prioritize lower-level solutions (escalation hierarchy)
        )

        ranked.append({
            "level": sol["level"],
            "text": sol["text"],
            "recency": recency,
            "success_rate": feedback_score,
            "score": final_score
        })

    return sorted(ranked, key=lambda x: x["score"], reverse=True)