"""Diff rendering utilities for comparing script versions.

Provides GitHub-style diff rendering with color highlighting
for comparing text versions side-by-side or inline.
"""
import difflib
from typing import Tuple
import html


def render_diff(old_text: str, new_text: str) -> str:
    """Generate HTML table diff with color highlighting.
    
    Creates a side-by-side comparison table with:
    - Green highlighting for additions
    - Red highlighting for deletions
    - Line numbers for both versions
    
    Args:
        old_text: Previous version of the text
        new_text: Current version of the text
        
    Returns:
        HTML string with styled diff table
    """
    differ = difflib.HtmlDiff(tabsize=4, wrapcolumn=40)
    return differ.make_table(
        old_text.splitlines(),
        new_text.splitlines(),
        fromdesc="Previous Version",
        todesc="Current Version",
        context=True,
        numlines=3,
    )


def render_inline_diff(old_text: str, new_text: str) -> str:
    """Generate inline diff with highlighted changes.
    
    Creates a unified diff view suitable for mobile screens with:
    - Lines prefixed with + (additions) or - (deletions)
    - Color highlighting via inline styles
    - More compact than side-by-side
    
    Args:
        old_text: Previous version of the text
        new_text: Current version of the text
        
    Returns:
        HTML string with styled inline diff
    """
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()
    
    differ = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile="Previous",
        tofile="Current",
        lineterm="",
    )
    
    html_lines = []
    html_lines.append('<div class="diff-inline" style="font-family: monospace; font-size: 0.9rem;">')
    
    for line in differ:
        escaped = html.escape(line)
        if line.startswith("+++") or line.startswith("---"):
            # File headers
            html_lines.append(f'<div style="color: #6b7280; font-weight: bold;">{escaped}</div>')
        elif line.startswith("@@"):
            # Chunk headers
            html_lines.append(f'<div style="color: #8b5cf6; background: rgba(139, 92, 246, 0.1); padding: 2px 8px; margin: 8px 0;">{escaped}</div>')
        elif line.startswith("+"):
            # Additions
            html_lines.append(f'<div style="background: rgba(34, 197, 94, 0.2); color: #16a34a; padding: 2px 8px;">{escaped}</div>')
        elif line.startswith("-"):
            # Deletions
            html_lines.append(f'<div style="background: rgba(239, 68, 68, 0.2); color: #dc2626; padding: 2px 8px;">{escaped}</div>')
        else:
            # Context lines
            html_lines.append(f'<div style="padding: 2px 8px;">{escaped}</div>')
    
    html_lines.append('</div>')
    return "\n".join(html_lines)


def get_diff_stats(old_text: str, new_text: str) -> Tuple[int, int]:
    """Calculate addition and deletion counts between versions.
    
    Args:
        old_text: Previous version of the text
        new_text: Current version of the text
        
    Returns:
        Tuple of (additions_count, deletions_count)
    """
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()
    
    differ = difflib.unified_diff(old_lines, new_lines, lineterm="")
    
    additions = 0
    deletions = 0
    
    for line in differ:
        if line.startswith("+") and not line.startswith("+++"):
            additions += 1
        elif line.startswith("-") and not line.startswith("---"):
            deletions += 1
    
    return additions, deletions
