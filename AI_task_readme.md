## STAR Cooperation – AI Team: Interview Test Exercise

### Use Case, Goal. Deliverables & Evaluation Criteria

#### Use Case:
STAR Cooperation has supported an OEM for many years by handling technical support tickets. Over time, all ticket interactions have been documented, resulting in an Excel file containing 6,000 historical tickets. The AI department has now been tasked with designing a chatbot that can generate solutions for new ticket requests based on these historical records and improves its recommendations based on user feedback.


#### Goal: Build a small end to end solution that:
- Provides a **frontend** (simple WEB UI of your choice) where a user can submit a support request in text form.
- Exposes a **backend** that reads from a provided Excel data source and returns a structured troubleshooting response.
- The "Learning" Loop: You must implement a feedback mechanism. If the system identifies multiple solutions (e.g., Solution 1, 2, and 3), the user should be able to "confirm/select" which solution worked on frontend.
- Implements and documents your own design choices for **matching, prioritization, evaluation of the output quality and guardrails**.
- Model Integration: You must use Ollama to run your Large Language Models locally. Please specify which model you selected.


#### Deliverables:
Submit **within 1 week** via our provided link after receiving the task:
- A runnable project (frontend + backend). You must be able to run it on your device to show us the solution on presentation day.
- A clear **README.md** describing setup and assumptions.
- A short **PowerPoint presentation (max 3 slides)** summarizing your solution for the AI team.

#### Evaluation Criteria:
We are specifically intrested with this part in your approach:  
Vector Search Quality: How well does the bot find relevant tickets? Which Stratergy was used and Why?  
Data Strategy: How do you handle the Solution 1 -> 2 -> 3 hierarchy?  
Feedback Integration: How do you update your "ranking" based on user confirmation?  
Response Quality: How did you evaluate the reponse quality?

### Data Source (Excel)
You will receive an Excel file with one sheet, where each row represents a ticket.
Representative columns include:
- id: Internal numbering within the Excel file 
- ticketID: Unique identifier of the ticket in the system 
- dateReceived1 / timeReceived1: Date and time when the ticket was first received 
- dateStart1 / timeStart1: Date and time when the ticket was first processed 
- dateFinished1 / timeFinished1: Date and time when the ticket was completed 
- solution1: First solution attempt 
- dateReceived2 / timeReceived2: Same as above for solution 2 (if solution 1 was insufficient) 
- solution2: Second solution attempt 
- dateReceived3 / timeReceived3: Same as above for solution 3 (rare cases) 
- solution3: Third solution attempt 
- systemName: Name of the system where the fault occurred 
- customerComplaint: Description of the customer’s issue 
- faultText: Fault message displayed in the system 
- recovery: Indicates recovery type: 
    - Soft Recovery (SR): Deletes customer system applications, requiring reinstallation
    - Full Recovery (FR): Resets the entire device to factory settings and reinstalls the OS
- exchange: Indicates whether the system had to be replaced 
- mainFault / subFault: Primary and detailed fault categories. Important for audit processes, not for the response.
- remote: Whether a remote session was required 
- refuel: Process of reinstalling the OS and recovery partition remotely 
- kw: Calendar week when the ticket was created

### Example Scenario:
To succeed, your system must handle the following workflow:

User Query: "System X is showing Error Y."

Initial Retrieval: The AI finds the most relevant historical ticket with mentioning the corresponding ticketID and prints all 3 solutions (if available) on the frontend.

User Action: The user reviews and tries the suggestions made and gives a feedback to the backend which solution worked for the user (lets assume solution 2 worked).

Persistence: The backend updates a backend source based on user feedback.

Adaptive Ranking: When a new user asks the same question later, your system should prioritize Solution 2 as the primary recommendation due to its past success.

### Notes
- The solution fields are independent. If the first solution fails, the ticket returns for a new attempt. Most tickets do not go beyond solution 2; solution 3 is rare.
- Recency matters: The newer the solution, the better, as systems are continuously updated.
- Expect missing or noisy values; handle parsing and normalization robustly (e.g., date formats).
- Fast response time is not critical since resources for local deployment are limited. However, you must be able to explain how to improve response quality without increasing resource capacity. 
- Consider only columns relevant to your approach.