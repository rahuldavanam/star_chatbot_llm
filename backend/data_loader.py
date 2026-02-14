import pandas as pd
from dateutil import parser
from datetime import datetime, time

def safe_datetime(date_val, time_val=None):
    """
    Safely parse date + optional time into a datetime.
    If time is missing, defaults to 00:00:00.
    Returns None if date parsing fails.
    """
    try:
        date_part = parser.parse(str(date_val)).date()
        if pd.notna(time_val):
            time_part = parser.parse(str(time_val)).time()
        else:
            time_part = time(0, 0, 0)
        return datetime.combine(date_part, time_part)
    except Exception:
        return None


def load_tickets(excel_path: str):
    """
    Load support tickets from an Excel file.

    Args:
        excel_path (str): Path to the Excel file.
    Returns:
        List of dictionaries representing support tickets.
    """
    df = pd.read_excel(excel_path)

    tickets = []

    for _, row in df.iterrows():
        problem_text = (
            f"System: {row.get('systemName', '')}\n"
            f"Fault: {row.get('faultText', '')}\n"
            f"Customer complaint: {row.get('customerComplaint', '')}"
        )

        ticket_datetime = safe_datetime(
            row.get("dateFinished"),
            row.get("timeFinished")
        )

        solutions = []

        for level in [1, 2, 3]:
            text = row.get(f"solution{level}")
            if pd.notna(text):
                solutions.append({
                    "level": level,
                    "text": str(text),
                    "date": safe_datetime(row.get(f"dateReceived{level}"), row.get(f"timeReceived{level}"))
                })

        tickets.append({
            "ticket_id": str(row.get("ticketID")),
            "system": row.get("systemName"),
            "problem_text": problem_text,
            "solutions": solutions,
            "finished_datetime": ticket_datetime
        })

    return tickets
