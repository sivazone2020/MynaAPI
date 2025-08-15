import os
from dotenv import load_dotenv
import pinecone

# Load environment variables from .env file
load_dotenv()

print("🔍 Debugging Pinecone Connection")
print("=" * 40)

# Load environment variables
api_key = os.getenv('PINECONE_API_KEY')
index_name = os.getenv('PINECONE_INDEX', 'mynaservice')
pinecone_host = os.getenv('PINECONE_HOST', '')
environment = os.getenv('PINECONE_ENVIRONMENT', '')

print(f"📊 API Key: {api_key[:20]}..." if api_key else "❌ No API Key found")
print(f"📑 Expected Index: {index_name}")
print(f"🏠 Host: {pinecone_host}")
print(f"🌍 Environment: {environment}")

try:
    print("\n🔧 Initializing Pinecone...")
    
    # Try multiple initialization approaches
    print("🔧 Attempt 1: Basic initialization")
    pinecone.init(api_key=api_key)
    print("✅ Pinecone initialized")
    
    # Check if we can see indexes
    print("📋 Listing all available indexes...")
    indexes = pinecone.list_indexes()
    print(f"📊 Found {len(indexes)} indexes: {indexes}")
    
    if len(indexes) == 0:
        print("\n🔧 Attempt 2: Initialize with environment (if needed)")
        # Some Pinecone accounts need environment specification
        try:
            # Let's try common environments
            environments = ['us-east-1-aws', 'us-west-1-aws', 'us-central1-gcp', 'asia-northeast1-gcp']
            for env in environments:
                try:
                    print(f"🔧 Trying environment: {env}")
                    pinecone.init(api_key=api_key, environment=env)
                    indexes = pinecone.list_indexes()
                    if len(indexes) > 0:
                        print(f"✅ Success with environment: {env}")
                        break
                except Exception as e:
                    print(f"❌ Failed with {env}: {e}")
                    continue
        except Exception as e:
            print(f"❌ Environment attempt failed: {e}")
    
    print(f"📊 Final index count: {len(indexes)}")
    for idx_name in indexes:
        print(f"  📌 Name: {idx_name}")
        # Get more details about each index
        try:
            idx_info = pinecone.describe_index(idx_name)
            print(f"      Details: {idx_info}")
        except Exception as e:
            print(f"      Error getting details: {e}")
        print("  " + "-" * 30)
    
    if index_name in indexes:
        print(f"✅ Target index '{index_name}' found!")
        
        # Try to connect to the index
        print(f"🔗 Connecting to index '{index_name}'...")
        index = pinecone.Index(index_name)
        print("✅ Index connection successful")
        
        print("📊 Getting index stats...")
        stats = index.describe_index_stats()
        print(f"📈 Index stats: {stats}")
        
        # Try a simple query
        print("🔍 Testing query functionality...")
        test_vector = [0.1] * 3072  # Test vector with correct dimensions
        results = index.query(vector=test_vector, top_k=3, include_metadata=True)
        print(f"✅ Query successful! Found {len(results.matches)} matches")
        
    else:
        print(f"❌ Target index '{index_name}' not found!")
        print(f"Available indexes: {indexes}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
