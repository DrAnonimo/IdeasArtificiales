from typing import Dict, Any, List
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .config import make_llm


SUMMARY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You summarize AI news for LinkedIn professionals. Focus on business impact, career relevance, and industry trends. 
    Output 5 parts:
    1. Title (engaging for LinkedIn)
    2. One-sentence Hook (why professionals should care)
    3. 3 Key Business Points (bullet points with metrics/impact)
    4. Career/Industry Impact (1-2 lines)
    5. Engagement Score (1-10) - based on: controversy, innovation, job relevance, business impact, trending topic
    
    Only use verifiable facts from the content."""),
    ("human", "Title: {title}\nURL: {url}\nContent: {content}\n\nReturn the LinkedIn-focused summary now.")
])


def summarize_results(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = make_llm()
    results: List[Dict[str, Any]] = state.get("results", [])
    if not results:
        return {**state, "summaries": []}

    # Take top N candidates
    top = results[:6]

    chain = SUMMARY_PROMPT | llm | StrOutputParser()

    summaries: List[Dict[str, Any]] = []
    for r in top:
        text = r.get("content") or ""
        if not text:
            continue
        summary = chain.invoke({
            "title": r.get("title", "(no title)"),
            "url": r.get("url", ""),
            "content": text[:6000],  # keep within token limits
        })
        summaries.append({
            "title": r.get("title"),
            "url": r.get("url"),
            "summary": summary,
            "source_content": text,
        })

    # Rank by LinkedIn engagement factors
    def score_linkedin_engagement(s: Dict[str, Any]) -> int:
        body = s.get("summary", "").lower()
        score = 0
        
        # High-impact business terms
        business_terms = ["%", "$", "billion", "million", "revenue", "profit", "growth", "market", "industry"]
        score += sum(2 for term in business_terms if term in body)
        
        # Career/job relevance
        career_terms = ["jobs", "career", "skills", "hiring", "salary", "opportunities", "training", "certification"]
        score += sum(3 for term in career_terms if term in body)
        
        # Innovation/trending
        innovation_terms = ["breakthrough", "revolutionary", "disrupt", "transform", "cutting-edge", "pioneer"]
        score += sum(2 for term in innovation_terms if term in body)
        
        # Controversy/discussion potential
        discussion_terms = ["debate", "controversy", "challenge", "concern", "risk", "ethics", "regulation"]
        score += sum(3 for term in discussion_terms if term in body)
        
        # Try to extract engagement score from summary
        import re
        engagement_match = re.search(r'engagement score[:\s]*(\d+)', body)
        if engagement_match:
            score += int(engagement_match.group(1)) * 2
        
        return score

    summaries = sorted(summaries, key=score_linkedin_engagement, reverse=True)[:3]

    return {**state, "summaries": summaries}
