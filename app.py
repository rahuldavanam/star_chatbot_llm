import streamlit as st
from backend.data_loader import load_tickets
from backend.embedding_search import VectorSearch
from backend.ranker import rank_solutions
from backend.feedback import init_db, record_success, record_failure
from backend.llm import generate_response

st.set_page_config(page_title="Support Assistant", layout="wide")

@st.cache_resource
def init():
    init_db()
    tickets = load_tickets("data/tickets_dataset.xlsx")
    return VectorSearch(tickets)

def handle_success(ticket_id, level):
    record_success(ticket_id, level)
    st.session_state.feedback_given = True
    st.session_state.solution_feedback[level] = "success"

def handle_failure(ticket_id, level):
    record_failure(ticket_id, level)
    st.session_state.feedback_given = True
    st.session_state.solution_feedback[level] = "failure"

store = init()

st.title("Technical Support Assistant")

query = st.text_area(
    "Describe your issue",
    placeholder="System X shows error Y..."
)

# Initialize session state keys
if "ticket" not in st.session_state:
    st.session_state.ticket = None
if "ranked" not in st.session_state:
    st.session_state.ranked = None
if "vector_final_score" not in st.session_state:
    st.session_state.vector_final_score = None
if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = False
if "feedback_result" not in st.session_state:
    st.session_state.feedback_result = None
if "solution_feedback" not in st.session_state:
    st.session_state.solution_feedback = {}

# Search button
if st.button("Find Solutions") and query.strip():
    results = store.search(query, k=1)

    if not results: # Guardrail for no similar tickets
        st.warning(
            "No similar tickets found. "
            "Please provide more details or contact support@example.com."
        )
        st.session_state.ticket = None
        st.session_state.ranked = None
        st.session_state.solution_feedback = {}
        st.stop()
    else:
        result = results[0]
        st.session_state.ticket = result["ticket"]
        st.session_state.vector_final_score = result["vector_final_score"]
        st.session_state.ranked = rank_solutions(
            st.session_state.ticket
        )

        # Reset feedback state on new search
        st.session_state.feedback_given = False
        st.session_state.solution_feedback = {}

# Render results from session state
if st.session_state.ticket is not None:
    ticket = st.session_state.ticket
    vector_final_score = st.session_state.vector_final_score
    ranked = st.session_state.ranked

    st.subheader("Matched Ticket")
    st.markdown(
        f"**Ticket ID:** {ticket['ticket_id']}  \n"
        f"**System:** {ticket['system']}  \n"
        f"**Similarity-Recency score:** {vector_final_score:.2f}"
    )

    st.subheader("AI-Generated Troubleshooting Response")
    with st.spinner("Generating troubleshooting response..."):
        response = generate_response(ticket, ranked)
    st.write(response)

    st.subheader("Recommended Solutions")

    for sol in ranked:
        with st.expander(f"Solution {sol['level']}"):
            st.write(sol["text"])
            st.caption(
                f"Recency: {sol['recency']:.2f} | "
                f"Success rate: {sol['success_rate']:.2f}"
            )

            col1, col2 = st.columns(2)

            with col1:
                st.button(
                    "This solution worked",
                    key=f"success_{ticket['ticket_id']}_{sol['level']}",
                    disabled=st.session_state.feedback_given,
                    on_click=handle_success,
                    args=(ticket["ticket_id"], sol["level"])
                )

            with col2:
                st.button(
                    "This solution didn't work",
                    key=f"failure_{ticket['ticket_id']}_{sol['level']}",
                    disabled=st.session_state.feedback_given,
                    on_click=handle_failure,
                    args=(ticket["ticket_id"], sol["level"])
                )

            if sol["level"] in st.session_state.solution_feedback:
                if st.session_state.solution_feedback[sol["level"]] == "success":
                    st.success("You marked this solution as successful.")
                else:
                    st.warning("You marked this solution as not working.")

    # Guardrail for overall failure feedback
    if st.button(
        "None of the solutions worked",
        disabled=st.session_state.feedback_given
    ):
        for sol in ranked:
            record_failure(ticket["ticket_id"], sol["level"])

        st.session_state.feedback_given = True
        st.session_state.solution_feedback = {
            sol["level"]: "failure" for sol in ranked
        }

        st.error(
            "Thanks for the feedback. This issue may require escalation "
            "or a newer solution."
        )