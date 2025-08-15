import os
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment variables from .env file
load_dotenv()

print("🔍 Debugging Pinecone Connection (v6.x API)")
print("=" * 50)

# Load environment variables
api_key = os.getenv('PINECONE_API_KEY')
index_name = os.getenv('PINECONE_INDEX', 'mynaservice')
pinecone_host = os.getenv('PINECONE_HOST', '')

print(f"📊 API Key: {api_key[:20]}..." if api_key else "❌ No API Key found")
print(f"📑 Expected Index: {index_name}")
print(f"🏠 Host: {pinecone_host}")

try:
    print("\n🔧 Initializing Pinecone (v6.x)...")
    
    # Initialize Pinecone using the new v6.x style
    pc = Pinecone(api_key=api_key)
    print("✅ Pinecone initialized")
    
    print("📋 Listing all available indexes...")
    indexes = pc.list_indexes()
    print(f"📊 Found {len(indexes)} indexes:")
    
    for idx in indexes:
        print(f"  📌 Name: {idx.name}")
        print(f"      Dimension: {idx.dimension}")
        print(f"      Metric: {idx.metric}")
        print(f"      Host: {idx.host}")
        print(f"      Status: {idx.status.ready}")
        print("  " + "-" * 30)
    
    # Check if our target index exists
    index_names = [idx.name for idx in indexes]
    if index_name in index_names:
        print(f"✅ Target index '{index_name}' found!")
        
        # Try to connect to the index
        print(f"🔗 Connecting to index '{index_name}'...")
        index = pc.Index(index_name)
        print("✅ Index connection successful")
        
        print("📊 Getting index stats...")
        stats = index.describe_index_stats()
        print(f"📈 Index stats: {stats}")
        
        # Try a simple query
        print("🔍 Testing query functionality...")
        test_vector = [0.1] * 3072  # Test vector with correct dimensions
        results = index.query(vector=test_vector, top_k=3, include_metadata=True)
        print(f"✅ Query successful! Found {len(results.matches)} matches")
        
        # Show some sample results
        for i, match in enumerate(results.matches[:3]):
            print(f"  🎯 Match {i+1}: Score={match.score:.4f}, ID={match.id}")
            if match.metadata:
                print(f"      Metadata: {match.metadata}")
        
    else:
        print(f"❌ Target index '{index_name}' not found!")
        print(f"Available indexes: {index_names}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
