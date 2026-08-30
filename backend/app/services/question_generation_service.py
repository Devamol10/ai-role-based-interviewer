import json
from typing import Dict, Any, List
from app.rag.retrieval import retrieve_relevant_chunks
from app.services.llm_service import call_llm

SYSTEM_PROMPT = """You are an expert technical interviewer conducting a role-based technical interview.
Your task is to generate one high-quality, personalized interview question for an engineering candidate.

STRICT CONSTRAINTS:
1. The question MUST be relevant to the candidate's target role.
2. The question MUST incorporate the candidate's specific technical background (skills/technologies).
3. The question MUST be grounded in the provided retrieved knowledge base context.
4. Do NOT hallucinate candidate experience not present in the profile.
5. Do NOT simply copy-paste text from the context; frame a clear conceptual or applied question.
6. Generate exactly ONE question.
7. Return a valid JSON object matching the requested format.
"""

def generate_interview_question(
    candidate_profile: Dict[str, Any],
    role: str,
    topic: str
) -> Dict[str, Any]:
    # 1. Build role + candidate + topic retrieval query
    skills_str = ", ".join(candidate_profile.get("skills", []))
    tech_str = ", ".join(candidate_profile.get("technologies", []))
    
    retrieval_query = f"{role} candidate experienced with {skills_str} {tech_str}. Interview topic: {topic}"

    # 2. Retrieve RAG knowledge chunks
    retrieved_chunks = retrieve_relevant_chunks(
        query=retrieval_query,
        role=role,
        top_k=3
    )

    context_str = "\n\n".join([f"Source ({c['source']}): {c['text']}" for c in retrieved_chunks])

    user_prompt = f"""
Target Role: {role}
Selected Topic: {topic}
Candidate Skills: {skills_str}
Candidate Technologies: {tech_str}
Candidate Summary: {candidate_profile.get('experience_summary', '')}

Retrieved Knowledge Base Context:
---
{context_str if context_str else "No additional domain knowledge retrieved."}
---

Generate ONE personalized interview question based on the topic and grounded in the retrieved context.

Return JSON object:
{{
  "question": "The question text",
  "topic": "{topic}",
  "difficulty": "Medium",
  "reason": "Short 1-sentence explanation of why this topic and question fit the candidate's profile"
}}
"""

    raw_response = call_llm(user_prompt, system_prompt=SYSTEM_PROMPT, json_mode=True)

    try:
        parsed = json.loads(raw_response)
        question_text = parsed.get("question", f"Can you explain key concepts of {topic} in your past projects?")
        difficulty = parsed.get("difficulty", "Medium")
        reason = parsed.get("reason", f"Selected based on {role} background.")
    except Exception:
        question_text = f"Based on your experience with {tech_str if tech_str else role}, how do you handle {topic} in production?"
        difficulty = "Medium"
        reason = f"Grounded in candidate's background with {topic}."

    return {
        "question": question_text,
        "topic": topic,
        "difficulty": difficulty,
        "reason": reason,
        "retrieved_context": retrieved_chunks
    }
