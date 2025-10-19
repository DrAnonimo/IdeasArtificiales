from typing import Dict, Any, List
import re
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .config import make_llm


POST_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert LinkedIn post writer for AI professionals. Create engaging, professional content that drives discussion and engagement.

    Structure (120-200 words):
    1. HOOK: Start with a compelling statement, statistic, or question that grabs attention
    2. INSIGHT: Share 1-2 key business insights or implications
    3. PERSONAL TOUCH: Add a brief professional perspective or experience
    4. CALL TO ACTION: End with a specific question or prompt for discussion
    5. ARTICLE LINK: Include the original article URL for readers to access the source
    6. HASHTAGS: 3-5 relevant hashtags

    Engagement tactics:
    - Use numbers, percentages, or specific metrics when available
    - Ask thought-provoking questions
    - Use "you" to address readers directly
    - Include industry-specific language
    - Create controversy or debate when appropriate
    - Use emojis sparingly (1-2 max)
    - Always include the article URL to help readers access the source

    Only use verifiable facts from the provided content. Do not invent metrics or dates."""),
    ("human", "Title: {title}\nURL: {url}\nExtracted Facts (verbatim):\n{facts}\n\nWrite an engaging LinkedIn post that will drive professional discussion and engagement. Make sure to include the article URL ({url}) in your post so readers can easily access the original source.")
])


def present_choices_for_human(state: Dict[str, Any]) -> Dict[str, Any]:
    return state  # No-op placeholder; CLI will handle printing and input


def extract_facts_from_summary(summary: str) -> List[str]:
    # Split bullet points and key statements into atomic facts
    bullets = re.findall(r"^-\s+.*$", summary, flags=re.MULTILINE)
    sentences = re.split(r"(?<=[.!?])\s+", summary)
    facts: List[str] = []
    for b in bullets:
        clean = b.strip("- ")
        if len(clean.split()) >= 3:
            facts.append(clean)
    for s in sentences:
        s = s.strip()
        if len(s.split()) >= 5 and s not in facts:
            facts.append(s)
    # Deduplicate and limit
    uniq: List[str] = []
    seen = set()
    for f in facts:
        if f not in seen:
            uniq.append(f)
            seen.add(f)
    return uniq[:12]


def generate_post(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = make_llm()
    chosen = state.get("chosen") or {}
    title = chosen.get("title", "")
    url = chosen.get("url", "")
    summary = chosen.get("summary", "")

    facts_list = extract_facts_from_summary(summary)
    facts_block = "\n".join(f"- {f}" for f in facts_list)

    chain = POST_PROMPT | llm | StrOutputParser()
    post = chain.invoke({
        "title": title,
        "url": url,
        "facts": facts_block,
    })

    return {**state, "post": post, "facts": facts_list}


def verify_post_against_facts(state: Dict[str, Any]) -> Dict[str, Any]:
    post: str = state.get("post", "")
    facts: List[str] = state.get("facts", [])
    iteration_count = state.get("iteration_count", 0)
    max_iterations = state.get("max_iterations", 3)
    hallucinations: List[str] = []

    # Check if we've reached max iterations
    if iteration_count >= max_iterations:
        report = {
            "ok": False,
            "missing_phrases": ["Maximum iterations reached"],
            "checked_phrases": [],
            "facts_used": facts,
            "max_iterations_reached": True,
            "message": "Reliable information not found"
        }
        return {**state, "verification": report, "iteration_count": iteration_count + 1}

    # Basic verification: every named entity-like capitalized multi-word phrase should be present in facts
    capital_phrases = re.findall(r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z0-9\-]+)+)\b", post)

    fact_text = " \n".join(facts).lower()
    for phrase in capital_phrases:
        if phrase.lower() not in fact_text:
            hallucinations.append(phrase)

    report = {
        "ok": len(hallucinations) == 0,
        "missing_phrases": hallucinations,
        "checked_phrases": capital_phrases,
        "facts_used": facts,
        "max_iterations_reached": False,
        "iteration": iteration_count + 1
    }
    
    return {**state, "verification": report, "iteration_count": iteration_count + 1}
