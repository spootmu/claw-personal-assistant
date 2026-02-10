import sys
import os
sys.path.insert(0, r'F:\AIP\claw-personal-assistant')

# Mock assistant object
class MockAssistant:
    def __init__(self):
        self.name = "Claw"
        self.memory_system = MockMemorySystem()

class MockMemorySystem:
    def __init__(self):
        self.database = MockDatabase()
    
    def store_community_insight(self, source, topic, insight):
        print(f"Storing insight from {source} about '{topic}'")

class MockDatabase:
    def get_unprocessed_community_insights(self):
        return []
    
    def search_learnings(self, topic, limit):
        return []

try:
    from community_integration import CommunityIntegration
    import asyncio
    
    print("Connecting to Moltbook community...")
    
    # Create mock assistant
    mock_assistant = MockAssistant()
    
    # Initialize community integration
    ci = CommunityIntegration(mock_assistant)
    
    print("Fetching latest insights from Moltbook...")
    
    # Run async function to get insights
    async def get_insights():
        return await ci.get_relevant_community_info("autonomous AI")
    
    insights = asyncio.run(get_insights())
    
    if insights:
        print(f"Retrieved {len(insights)} insights from Moltbook:")
        for i, insight in enumerate(insights):
            print(f"{i+1}. Source: {insight.get('source', 'N/A')}")
            print(f"   Topic: {insight.get('topic', 'N/A')}")
            print(f"   Content: {insight.get('content', 'N/A')[:100]}...")
            print()
    else:
        print("No new insights retrieved from Moltbook.")
        
except Exception as e:
    print(f"Error: {e}")
    
    # Fallback: Direct API access
    try:
        import aiohttp
        import asyncio
        
        async def check_moltbook_api():
            headers = {"Authorization": "Bearer moltbook_sk_bDr2P2t1FDj5Nxq8dzpk8M4DLdLkvyat"}
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get("https://www.moltbook.com/api/v1/feed?sort=new&limit=3", headers=headers) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            posts = data.get('posts', [])
                            print(f"Direct connection to Moltbook successful. Retrieved {len(posts)} recent posts:")
                            
                            for i, post in enumerate(posts[:3]):
                                title = post.get('title', 'No Title')
                                content = post.get('content', '')[:100]
                                author = post.get('author', {}).get('username', 'Unknown')
                                print(f"{i+1}. {title}")
                                print(f"   By: {author}")
                                print(f"   Preview: {content}...")
                                print()
                        else:
                            print(f"Moltbook API returned status {resp.status}")
                            print("Response:", await resp.text())
                except aiohttp.ClientConnectorError:
                    print("Could not connect to Moltbook - network error")
                except Exception as req_error:
                    print(f"Request error: {req_error}")
        
        asyncio.run(check_moltbook_api())
    except Exception as api_error:
        print(f"Could not access Moltbook API directly: {api_error}")