import json
from typing import List, Dict, Any
from app.services.llm_service import call_llm

DEFAULT_TOPICS_BY_ROLE = {
    "Backend Engineer": ["Database Performance", "API Design", "Caching Strategies", "Scalability & Architecture"],
    "AI/ML Engineer": ["Supervised Learning", "Model Evaluation & Metrics", "Neural Network Optimization", "Transformer Architectures"],
    "Data Science / Applied ML": ["Feature Engineering", "Statistical Hypothesis Testing", "Model Validation", "Exploratory Data Analysis"]
}

SYSTEM_PROMPT = """You are an expert technical interviewer selecting relevant interview topics.
Your job is to select 3-5 specific technical interview topics based on the candidate's profile and target role.
Return a valid JSON object with a "topics" list of strings.
"""

def select_interview_topics(profile: Dict[str, Any], role: str) -> List[str]:
    user_prompt = f"""Target Role: {role}
Candidate Profile:
- Skills: {', '.join(profile.get('skills', []))}
- Technologies: {', '.join(profile.get('technologies', []))}
- Summary: {profile.get('experience_summary', '')}

Select 3 to 5 appropriate interview topics for this candidate and role.
Return JSON format: {{"topics": ["Topic 1", "Topic 2", ...]}}
"""

    try:
        raw_response = call_llm(user_prompt, system_prompt=SYSTEM_PROMPT, json_mode=True)
        data = json.loads(raw_response)
        topics = data.get("topics", [])
        if isinstance(topics, list) and len(topics) > 0:
            return [str(t) for t in topics[:5]]
    except Exception:
        pass

    # Fallback to default topics by role if LLM call is unconfigured or fails
    return DEFAULT_TOPICS_BY_ROLE.get(role, ["System Design", "Core Concepts", "Problem Solving"])
