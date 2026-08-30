import json
from typing import Dict, Any, List
from app.services.llm_service import call_llm

def get_recommendation_label(score: float) -> str:
    """
    Deterministic candidate recommendation thresholds.
    """
    if score >= 8.5:
        return "Strong Candidate"
    elif score >= 7.0:
        return "Good Candidate"
    elif score >= 5.0:
        return "Needs Improvement"
    else:
        return "Significant Gaps"

def generate_summary(
    role: str,
    overall_score: float,
    qa_evaluations: List[Dict[str, Any]],
    strengths: List[str],
    weaknesses: List[str]
) -> str:
    eval_details = []
    for idx, item in enumerate(qa_evaluations, 1):
        eval_details.append(
            f"Q{idx} ({item.get('topic', '')}): Score {item.get('score', 0)}/10\n"
            f"Feedback: {item.get('feedback', '')}"
        )
    
    details_str = "\n\n".join(eval_details)

    system_prompt = """You are a senior technical hiring manager writing a concise executive candidate assessment.
Summarize ONLY the provided interview performance details objectively.
Do NOT invent candidate experience or make non-technical judgments.
Keep the summary under 4 sentences.
"""

    user_prompt = f"""
Candidate Target Role: {role}
Overall Score: {overall_score} / 10

Per-Question Breakdown:
{details_str}

Identified Strengths: {', '.join(strengths) if strengths else 'None identified'}
Identified Areas to Improve: {', '.join(weaknesses) if weaknesses else 'None identified'}

Write a professional, concise executive summary of the candidate's interview performance.
Return JSON: {{"summary": "The candidate demonstrated strong..."}}
"""

    try:
        raw_response = call_llm(user_prompt, system_prompt=system_prompt, json_mode=True)
        parsed = json.loads(raw_response)
        if parsed.get("summary"):
            return str(parsed["summary"])
    except Exception:
        pass

    return f"The candidate achieved an overall score of {overall_score:.1f}/10 for the {role} position across 5 evaluated technical topics."
