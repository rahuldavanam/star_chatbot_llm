from math import sqrt
import sqlite3
from datetime import datetime


DB_PATH = "data/feedback.db"

def wilson_score(success, attempts, z=1.96):
    """
    Compute Wilson lower bound score.

    Args:
        success (int): Number of successful outcomes.
        attempts (int): Total attempts.
        z (float): Z-score for confidence level (1.96 ≈ 95%).

    Returns:
        float: Wilson score between 0 and 1.
    """
    if attempts == 0:
        return 0.0

    p = success / attempts

    denominator = 1 + (z**2 / attempts)  # Normalization factor
    centre = p + (z**2 / (2 * attempts)) # Adjustment term
    margin = z * sqrt((p * (1 - p) + (z**2 / (4 * attempts))) / attempts)  # Uncertain penalty

    return (centre - margin) / denominator

def init_db():
    """
    Initialize the feedback database and create the feedback table if it doesn't exist.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        ticket_id TEXT,
        solution_level INTEGER,
        success_count INTEGER,
        attempt_count INTEGER,
        last_updated TEXT,
        PRIMARY KEY (ticket_id, solution_level)
    )
    """)
    conn.commit()
    conn.close()


def record_success(ticket_id, solution_level):
    """
    Record a successful solution attempt for a given ticket and solution level.
    
    Args:
        ticket_id (str): The ID of the support ticket.
        solution_level (int): The level of the solution provided.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO feedback VALUES (?, ?, 1, 1, ?)
    ON CONFLICT(ticket_id, solution_level)
    DO UPDATE SET
        success_count = success_count + 1,
        attempt_count = attempt_count + 1,
        last_updated = ?
    """, (ticket_id, solution_level, datetime.utcnow().isoformat(),
          datetime.utcnow().isoformat()))

    conn.commit()
    conn.close()

def record_failure(ticket_id, solution_level):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO feedback VALUES (?, ?, 0, 1, ?)
    ON CONFLICT(ticket_id, solution_level)
    DO UPDATE SET
        attempt_count = attempt_count + 1,
        last_updated = ?
    """, (ticket_id, solution_level, datetime.utcnow().isoformat(),
          datetime.utcnow().isoformat()))

    conn.commit()
    conn.close()

def get_feedback(ticket_id, solution_level):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    SELECT success_count, attempt_count FROM feedback
    WHERE ticket_id=? AND solution_level=?
    """, (ticket_id, solution_level))
    row = cur.fetchone()
    conn.close()

    if row:
        return wilson_score(row[0], row[1])
    else:
        return 0.0