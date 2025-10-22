#!/usr/bin/env python3
"""
LangGraph workflow visualization using Graphviz
Shows the complete workflow with feedback loop and iteration tracking
"""

import graphviz
from graphviz import Digraph

def create_langgraph_workflow():
    """Create the main LangGraph workflow diagram"""
    
    # Create directed graph
    dot = Digraph(comment='LangGraph LinkedIn News Agent Workflow')
    dot.attr(rankdir='TB', size='16,12', dpi='300')
    dot.attr('node', shape='box', style='rounded,filled', fontname='Arial', fontsize='10')
    dot.attr('edge', fontname='Arial', fontsize='9')
    
    # Define node styles
    start_style = {'shape': 'ellipse', 'color': '#2E8B57', 'fillcolor': '#90EE90', 'style': 'filled'}
    process_style = {'shape': 'box', 'style': 'rounded,filled', 'fillcolor': '#E6F3FF'}
    decision_style = {'shape': 'diamond', 'color': '#FF8C00', 'fillcolor': '#FFE4B5', 'style': 'filled'}
    error_style = {'shape': 'box', 'color': '#8B0000', 'fillcolor': '#FFB6C1', 'style': 'filled'}
    end_style = {'shape': 'ellipse', 'color': '#DC143C', 'fillcolor': '#FFA0A0', 'style': 'filled'}
    
    # Add nodes with enhanced styling
    dot.node('START', 'START', **start_style)
    dot.node('search', 'Search AI News\n\n• Tavily API calls\n• Business queries\n• Raw articles', **process_style)
    dot.node('summarize', 'Summarize Results\n\n• LLM processing\n• LinkedIn scoring\n• Engagement ranking', **process_style)
    dot.node('human_choice', 'Human Choice\n\n• CLI display\n• User selection\n• Chosen article', **decision_style)
    dot.node('generate_post', 'Generate LinkedIn Post\n\n• Professional structure\n• Hook + CTA\n• Hashtags', **process_style)
    dot.node('verify', 'Verify Facts\n\n• Fact checking\n• Hallucination detection\n• Iteration count', **process_style)
    dot.node('decision', 'Verification\nOK?', **decision_style)
    dot.node('max_iter', 'Max Iterations\nReached?', **decision_style)
    dot.node('error', 'Reliable Information\nNot Found\n\n• After 3 iterations\n• Cannot verify facts\n• Do NOT suggest article', **error_style)
    dot.node('END', 'END\n\n• Final post + tips\n• Verification report', **end_style)
    
    # Add edges with labels and styling
    dot.edge('START', 'search', 'queries', color='green', penwidth='2')
    dot.edge('search', 'summarize', 'articles', color='blue', penwidth='2')
    dot.edge('summarize', 'human_choice', 'summaries', color='orange', penwidth='2')
    dot.edge('human_choice', 'generate_post', 'chosen', color='purple', penwidth='2')
    dot.edge('generate_post', 'verify', 'post', color='pink', penwidth='2')
    dot.edge('verify', 'decision', 'verification\nresult', color='gray', penwidth='2')
    
    # Decision paths
    dot.edge('decision', 'END', 'OK', color='green', penwidth='3', style='bold')
    dot.edge('decision', 'max_iter', 'FAIL', color='red', penwidth='2')
    
    # Feedback loop
    dot.edge('max_iter', 'generate_post', 'regenerate\n(if < 3 iterations)', color='red', penwidth='2', style='dashed')
    dot.edge('max_iter', 'error', 'max reached\n(= 3 iterations)', color='red', penwidth='2', style='bold')
    dot.edge('error', 'END', 'error message', color='red', penwidth='2')
    
    # Add subgraph for feedback loop
    with dot.subgraph(name='cluster_feedback') as c:
        c.attr(style='filled', color='lightgray', label='Feedback Loop (Max 3 Iterations)')
        c.attr(rank='same')
        c.node('generate_post')
        c.node('verify')
        c.node('decision')
        c.node('max_iter')
    
    # Add subgraph for data flow
    with dot.subgraph(name='cluster_data') as d:
        d.attr(style='filled', color='lightblue', label='Data Flow')
        d.attr(rank='same')
        d.node('search')
        d.node('summarize')
        d.node('human_choice')
    
    return dot

def main():
    """Generate the main workflow diagram"""
    
    print("Generating LangGraph workflow diagram...")
    
    # Main workflow diagram
    workflow_dot = create_langgraph_workflow()
    workflow_dot.render('langgraph_workflow', format='png', cleanup=True)
    workflow_dot.render('langgraph_workflow', format='svg', cleanup=True)
    print("✅ LangGraph workflow diagram saved as 'langgraph_workflow.png' and 'langgraph_workflow.svg'")
    print("\n🎉 Workflow diagram generated successfully!")

if __name__ == "__main__":
    main()