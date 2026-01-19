from memory.brain_limbic import NexusMemory
import time

def test_hippocampus():
    print("Initializing Hippocampus (NexusMemory)...")
    brain = NexusMemory()
    
    # 1. Test Adding Memories
    print("\n[TEST] Encoding memories...")
    brain.add_memory("My name is Siddi Vinayaka.", type="fact", importance=1.0)
    brain.add_memory("I am working on upgrading Nexus AI.", type="episodic", importance=0.8)
    brain.add_memory("The sky is blue.", type="semantic", importance=0.1)
    
    print("Memories stored.")
    
    # 2. Test Recall
    query = "Who is Siddi?"
    print(f"\n[TEST] Recalling: '{query}'")
    results = brain.recall(query, k=2)
    
    for r in results:
        print(f" - Found: {r['content']} (Score: {r['score']:.4f})")
        
    # Verify
    if any("Siddi" in r['content'] for r in results):
        print("\nSUCCESS: Memory recall functional.")
    else:
        print("\nFAILURE: Could not recall name.")

if __name__ == "__main__":
    test_hippocampus()
