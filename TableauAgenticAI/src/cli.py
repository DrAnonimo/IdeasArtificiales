import json
from typing import Dict, Any
from rich import print as rprint
from rich.table import Table
from rich.prompt import Prompt

from .app import build_workflow


def run():
    try:
        app = build_workflow()
    except RuntimeError as e:
        rprint(f"[bold red]Configuration Error: {e}[/bold red]")
        rprint("[yellow]Please set your API keys in environment variables or .env file[/yellow]")
        return

    # Phase 1: search + summarize
    state: Dict[str, Any] = {
        "queries": [
            "AI business impact 2024", "AI productivity tools", "AI job market trends", 
            "AI startup funding", "AI enterprise adoption", "AI career opportunities",
            "AI automation success stories", "AI industry disruption", "AI skills demand"
        ],
        "results": [],
        "summaries": [],
        "chosen": {},
        "post": "",
        "facts": [],
        "verification": {},
        "iteration_count": 0,
        "max_iterations": 3
    }

    rprint("[bold cyan]Searching and summarizing AI news...[/bold cyan]")
    try:
        state = app.invoke(state, config={"configurable": {"thread_id": "ai-news"}})
    except Exception as e:
        rprint(f"[bold red]Error during search/summarize: {e}[/bold red]")
        return

    summaries = state.get("summaries", [])
    if not summaries:
        rprint("[bold red]No summaries found. Try again later.[/bold red]")
        return

    # Display summaries for human selection
    rprint("\n[bold cyan]🔥 Top AI News for LinkedIn Engagement[/bold cyan]")
    rprint("[yellow]Select the most engaging story for your professional network:[/yellow]\n")
    
    for idx, s in enumerate(summaries, start=1):
        title = s.get("title", "(no title)")
        summary = s.get("summary", "")
        url = s.get("url", "")
        
        rprint(f"[bold green]Option {idx}:[/bold green] {title}")
        rprint(f"[blue]URL:[/blue] {url}")
        rprint(f"[white]Summary:[/white] {summary[:400]}{'...' if len(summary) > 400 else ''}")
        rprint("-" * 80)

    choice = Prompt.ask("Select the most exciting (1-3)", choices=["1", "2", "3"], default="1")
    chosen = summaries[int(choice) - 1]

    # Phase 2: generate LinkedIn post + verify (with feedback loop)
    rprint("[bold cyan]Generating LinkedIn post and verifying...[/bold cyan]")

    state.update({"chosen": chosen})
    
    # Run the generation and verification loop
    max_iterations = 3
    for iteration in range(max_iterations):
        rprint(f"[yellow]Iteration {iteration + 1}/{max_iterations}: Generating and verifying post...[/yellow]")
        
        state = app.invoke(state, config={"configurable": {"thread_id": "ai-news"}})
        
        verification = state.get("verification", {})
        iteration_count = state.get("iteration_count", 0)
        
        if verification.get("ok", False):
            rprint(f"[green]✅ Post verified successfully on iteration {iteration_count}![/green]")
            break
        elif verification.get("max_iterations_reached", False):
            rprint(f"[red]❌ Maximum iterations ({max_iterations}) reached. Reliable information not found.[/red]")
            break
        else:
            missing_phrases = verification.get("missing_phrases", [])
            rprint(f"[yellow]⚠️  Verification failed. Missing phrases: {missing_phrases}[/yellow]")
            rprint(f"[yellow]🔄 Regenerating post...[/yellow]")

    post = state.get("post", "")
    verification = state.get("verification", {})

    rprint("\n" + "="*80)
    
    if verification.get("max_iterations_reached", False):
        rprint("[bold red]❌ RELIABLE INFORMATION NOT FOUND[/bold red]")
        rprint("="*80)
        rprint("The system was unable to generate a factually reliable LinkedIn post")
        rprint("after 3 iterations of verification. This may be due to:")
        rprint("• Insufficient factual content in the source article")
        rprint("• Complex claims that cannot be easily verified")
        rprint("• Limited source material for fact-checking")
        rprint("\n[yellow]Recommendation: Try selecting a different news article with more concrete facts.[/yellow]")
    else:
        rprint("[bold green]📝 YOUR LINKEDIN POST[/bold green]")
        rprint("="*80)
        rprint(post)
        rprint("="*80)
        
        # Show the article URL for reference
        chosen_article = state.get("chosen", {})
        article_url = chosen_article.get("url", "")
        if article_url:
            rprint(f"\n[bold cyan]🔗 Original Article:[/bold cyan] {article_url}")
            rprint("[dim]Note: The article link is included in the post above for easy access[/dim]")
        
        rprint("\n[bold yellow]📊 Engagement Analysis[/bold yellow]")
        if verification.get("ok"):
            rprint("✅ [green]Post verified - all claims are fact-checked[/green]")
        else:
            rprint("⚠️  [yellow]Some phrases need verification:[/yellow]")
            for phrase in verification.get("missing_phrases", []):
                rprint(f"   - {phrase}")
        
        rprint(f"\n[bold blue]💡 Pro Tips for Maximum Engagement:[/bold blue]")
        rprint("• Post during business hours (9 AM - 5 PM)")
        rprint("• Engage with comments within the first hour")
        rprint("• Tag relevant professionals in comments")
        rprint("• Share in relevant LinkedIn groups")
        rprint("• Consider creating a follow-up post with your experience")
        rprint("• The article link helps readers access the source easily")


if __name__ == "__main__":
    run()
