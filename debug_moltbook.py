from social.moltbook_client import get_moltbook_client
import json

def test_moltbook():
    client = get_moltbook_client()
    print(f"Agent Name: {client.agent_name}")
    print(f"API Key: {client.api_key}")
    print(f"Claimed: {client.is_claimed}")
    
    if not client.api_key:
        print("No API Key found. Cannot test.")
        return

    # 1. Check Status
    print("\n--- Checking Status ---")
    status = client.check_status()
    print(f"Status Response: {json.dumps(status, indent=2)}")
    
    # 2. Try to fetch own profile
    print("\n--- Fetching Profile ---")
    profile = client.get_profile()
    print(f"Profile Response: {json.dumps(profile, indent=2)}")

    # 3. Test Post (only if claimed)
    if client.is_claimed:
        print("\n--- Attempting Test Post ---")
        post_res = client.post("Debug Post via Script", "Testing Moltbook API connectivity from debug script.", submolt="general")
        print(f"Post Response: {json.dumps(post_res, indent=2)}")
    else:
        print("\nAgent not claimed. Skipping post test.")

    # 4. Check User Posts (Alternative Endpoint)
    print("\n--- Checking User Posts (Alternative) ---")
    # Trying generic posts endpoint with author filter
    alt_posts = client._request("GET", f"/posts?author={client.agent_name}&limit=10")
    print(f"Alt User Posts Response: {json.dumps(alt_posts, indent=2)}")

if __name__ == "__main__":
    test_moltbook()
