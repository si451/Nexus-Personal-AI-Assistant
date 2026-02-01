
"""
Skill: GitHub Integration
=========================
Allows Nexus to interact with GitHub Repositories.
Ported from OpenClaw's 'github' skill (originally using `gh` CLI),
re-implemented using PyGithub for better Python integration.
"""

import os
from github import Github
from skills.loader import skill
from typing import Optional

def _get_github_client():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return None, "Error: GITHUB_TOKEN not found in environment variables."
    return Github(token), None

@skill
def github_list_issues(repo_name: str, state: str = "open", limit: int = 5):
    """
    List issues from a GitHub repository.
    
    Args:
        repo_name: Full repository name (e.g., 'openclaw/openclaw')
        state: 'open' or 'closed'
        limit: Number of issues to return
    """
    g, err = _get_github_client()
    if err: return err
    
    try:
        repo = g.get_repo(repo_name)
        issues = repo.get_issues(state=state)
        
        summary = f"**Issues in {repo_name} ({state}):**\n"
        count = 0
        for issue in issues:
            if count >= limit: break
            summary += f"- #{issue.number}: {issue.title} (by @{issue.user.login})\n"
            count += 1
            
        return summary
    except Exception as e:
        return f"GitHub API Error: {str(e)}"

@skill
def github_read_issue(repo_name: str, issue_number: int):
    """
    Read the full content and comments of a specific issue.
    """
    g, err = _get_github_client()
    if err: return err
    
    try:
        repo = g.get_repo(repo_name)
        issue = repo.get_issue(issue_number)
        
        content = f"**#{issue.number}: {issue.title}**\n"
        content += f"Status: {issue.state}\n"
        content += f"Author: @{issue.user.login}\n\n"
        content += f"{issue.body}\n\n"
        content += "**Comments:**\n"
        
        for comment in issue.get_comments():
            content += f"--- @{comment.user.login}: ---\n{comment.body}\n"
            
        return content
    except Exception as e:
        return f"GitHub API Error: {str(e)}"

@skill
def github_search_repos(query: str, limit: int = 5):
    """
    Search for repositories on GitHub.
    Useful for finding new tools or libraries.
    """
    g, err = _get_github_client()
    if err: return err
    
    try:
        repos = g.search_repositories(query)
        summary = f"**Search Results for '{query}':**\n"
        
        count = 0
        for repo in repos:
            if count >= limit: break
            summary += f"- {repo.full_name}: {repo.description} (⭐ {repo.stargazers_count})\n"
            count += 1
            
        return summary
    except Exception as e:
        return f"GitHub API Error: {str(e)}"
