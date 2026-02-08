
from skills.loader import skill
from social import get_moltbook_client

@skill
def manage_moltbook(action: str, target: str = None, content: str = None):
    """
    Full access to Moltbook Social Media.
    
    Args:
        action: What to do.
            - "check_feed": See hot posts.
            - "my_posts": See posts I created.
            - "notifications": Check comments on MY posts.
            - "read_comments": Read comments on a specific post (target=post_id).
            - "user_posts": See another user's posts (target=username).
            - "follow": Follow a user (target=username).
            - "like": Like a post (target=post_id).
            - "reply": Comment on a post (target=post_id, content=your_text).
        target: The Post ID or Username (depends on action).
        content: The text content (only for 'reply').
    """
    client = get_moltbook_client()
    
    if not client.api_key:
        return "I am not registered on Moltbook yet."

    try:
        if action == "check_feed":
            feed = client.get_feed(limit=5)
            print(f"DEBUG: Feed Type: {type(feed)}")
            print(f"DEBUG: Feed Content: {feed}")
            return _format_feed(feed, "Global Feed")
            
        elif action == "my_posts":
            if not client.agent_name:
                return "I don't know my own username yet."
            posts = client.get_user_posts(client.agent_name)
            
            # Use Official Profile URL format per docs
            profile_url = f"https://www.moltbook.com/u/{client.agent_name}"
            return _format_feed(posts, f"Posts by @{client.agent_name}\nProfile: {profile_url}")

        elif action == "follow":
            if not target: return "Please provide a username to follow."
            if hasattr(client, "follow_user"):
                res = client.follow_user(target)
                if res.get("success"): return f"Successfully followed @{target}!"
                return f"Could not follow: {res.get('error')}"
            return "Follow feature not available."

        elif action == "like":
            if not target: return "Please provide a Post ID to like."
            res = client.upvote_post(target)
            if res.get("success"): return f"Liked post {target} ❤️"
            return "Could not like post."

        elif action == "reply":
            if not target or not content:
                 return "For reply, provide 'target' (post_id) and 'content' (your text)."
            res = client.comment(target, content)
            if res.get("success"): 
                url = f"https://www.moltbook.com/post/{target}"
                return f"Replied to {target}!\nView at: {url}"
            return f"Reply failed: {res.get('error')}"
            
        elif action == "notifications":
            # Simulate notifications by checking comments on my last 5 posts
            if not client.agent_name:
                return "Unknown username."
            
            my_posts = client.get_user_posts(client.agent_name, limit=5)
            posts_data = my_posts.get("data", {}).get("posts", [])
            
            if not posts_data:
                return "I haven't posted anything yet, so no notifications."
                
            notifs = []
            for post in posts_data:
                pid = post.get("id")
                # Get comments for this post
                comments_resp = client.get_comments(pid)
                comments = comments_resp.get("data", {}).get("comments", [])
                
                # Filter for recent? For now just show all new ones
                if comments:
                    p_title = post.get("title", "Untitled")
                    notifs.append(f"On **'{p_title}'**:")
                    for c in comments[:3]:
                        a_val = c.get('author')
                        a_name = a_val.get('name', 'Unknown') if isinstance(a_val, dict) else str(a_val)
                        notifs.append(f"  - @{a_name}: {c.get('content')}")
            
            return "\n".join(notifs) if notifs else "No new comments on your recent posts."
            
        elif action == "read_comments":
            if not target:
                return "Please provide a Post ID to read comments for."
            resp = client.get_comments(target)
            comments = resp.get("data", {}).get("comments", [])
            if not comments: return "No comments yet."
            
            out = [f"**Comments on {target[:8]}...**"]
            for c in comments[:10]:
                 a_val = c.get('author')
                 a_name = a_val.get('name', 'Unknown') if isinstance(a_val, dict) else str(a_val)
                 out.append(f"- **@{a_name}**: {c.get('content')}")
            return "\n".join(out)
            
        elif action == "user_posts":
            if not target: return "Please provide a username."
            posts = client.get_user_posts(target)
            return _format_feed(posts, f"Posts by @{target}")
            
        else:
            return f"Unknown action: {action}"
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Moltbook Error: {e}"

def _format_feed(response, title):
    if isinstance(response, str):
        return f"Error fetching {title}: {response}"
    if not isinstance(response, dict):
        return f"Error: Invalid response type ({type(response)}) from Moltbook client."
        
    # Check for error
    if response.get("success") == False:
        return f"Error: {response.get('error', 'Unknown error')}"
    
    # Handle different response formats - API may return posts at different levels
    posts = response.get("posts", [])
    if not posts:
        posts = response.get("data", {}).get("posts", [])
    if not posts:
        # Try recentPosts for profile responses
        posts = response.get("recentPosts", [])
        
    if not posts: 
        return f"{title}: No posts found."
    
    out = [f"## {title}"]
    for p in posts:
        post_id = p.get('id', '')
        post_url = f"https://www.moltbook.com/post/{post_id}" if post_id else "N/A"
        
        out.append(f"\n**{p.get('title', 'Untitled')}** (ID: {post_id})")
        
        # Handle author - can be string or object
        author = p.get('author')
        if isinstance(author, dict):
             author_name = author.get('name', 'Unknown')
        else:
             author_name = str(author) if author else "Unknown"
             
        karma = p.get('karma', p.get('upvotes', 0))
        comment_count = p.get('comment_count', len(p.get('comments', [])))
        
        out.append(f"By @{author_name} | ❤️ {karma} | 💬 {comment_count}")
        out.append(f"👉 {post_url}")
    return "\n".join(out)
