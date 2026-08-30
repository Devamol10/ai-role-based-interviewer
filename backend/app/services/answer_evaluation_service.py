import json
from typing import Dict, Any, List
from app.services.llm_service import call_llm

RUBRIC = """EVALUATION RUBRIC (0-10):
0-2: Incorrect or largely irrelevant.
3-4: Limited understanding with significant technical gaps.
5-6: Basic understanding with meaningful gaps or missing details.
7-8: Good understanding with minor gaps or slight trade-off oversights.
9-10: Strong, comprehensive, and technically accurate answer.
"""

SYSTEM_PROMPT = f"""You are an expert technical interviewer evaluating a candidate's answer.
Your task is to grade the response objectively based strictly on what the candidate actually wrote and grounded in the retrieved technical context.

{RUBRIC}

STRICT CONSTRAINTS:
1. Evaluate ONLY what the candidate actually wrote. Do NOT infer or hallucinate candidate knowledge.
2. The score MUST be an integer or single decimal float between 0 and 10 according to the rubric.
3. The retrieved context is a grounding reference; do NOT demand exact wording from the knowledge base. Correct phrasing in the candidate's own words should be scored high.
4. Return a valid JSON object matching the requested schema.
"""

def evaluate_answer(
    question_text: str,
    answer_text: str,
    role: str,
    topic: str,
    retrieved_context: List[Dict[str, Any]]
) -> Dict[str, Any]:
    if not answer_text or not answer_text.strip():
        return {
            "score": 0.0,
            "feedback": "No answer provided.",
            "strengths": [],
            "improvements": ["Provide a detailed technical answer."]
        }

    context_str = "\n\n".join([f"Source ({c.get('source', 'kb')}): {c.get('text', '')}" for c in retrieved_context])

    user_prompt = f"""
Target Role: {role}
Topic: {topic}

Interview Question:
"{question_text}"

Candidate Answer:
"{answer_text}"

Retrieved Grounding Context:
---
{context_str if context_str else "No additional domain context."}
---

Evaluate the candidate's answer and return a JSON object:
{{
  "score": 7.5,
  "feedback": "Clear explanation of core indexing concepts with a practical approach, though trade-offs could be discussed.",
  "strengths": [
    "Understood core concept of indexing",
    "Correctly identified query lookup benefits"
  ],
  "improvements": [
    "Discuss write overhead and index maintenance trade-offs"
  ]
}}
"""

    try:
        raw_response = call_llm(user_prompt, system_prompt=SYSTEM_PROMPT, json_mode=True)
        parsed = json.loads(raw_response)
        
        raw_score = float(parsed.get("score", 5.0))
        score = max(0.0, min(10.0, raw_score))
        
        return {
            "score": round(score, 1),
            "feedback": str(parsed.get("feedback", "Answer recorded.")),
            "strengths": [str(s) for s in parsed.get("strengths", [])],
            "improvements": [str(i) for i in parsed.get("improvements", [])]
        }
    except Exception as e:
        # Fallback evaluation on LLM failure - preserves candidate answer without losing state
        return {
            "score": 5.0,
            "feedback": "Answer recorded successfully (AI evaluation pending).",
            "strengths": ["Submitted technical answer."],
            "improvements": ["Detailed feedback unavailable."]
        }
