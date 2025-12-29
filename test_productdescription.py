"""
Test script for the Product/Service Description endpoint
Run the FastAPI server first: uvicorn backend.app:app --reload
Then run this script: python test_productdescription.py
"""

import requests
import json

# API endpoint
API_URL = "http://127.0.0.1:8000/productdescription"

# Test cases
test_cases = [
    {
        "name": "Luxury Restaurant in Dubai",
        "payload": {
            "industry": "Fine Dining Restaurant",
            "business_model": "Premium B2C dining experience with signature dishes",
            "language": "English"
        }
    },
    {
        "name": "Tech Startup B2B Service",
        "payload": {
            "industry": "Software as a Service (SaaS)",
            "business_model": "B2B cloud-based business management platform",
            "language": "English"
        }
    },
    {
        "name": "Café in Arabic",
        "payload": {
            "industry": "Coffee Shop",
            "business_model": "Casual café with specialty coffee and pastries",
            "language": "Arabic"
        }
    },
    {
        "name": "E-commerce Platform",
        "payload": {
            "industry": "Retail E-commerce",
            "business_model": "Online marketplace for local artisans and craftspeople",
            "language": "English"
        }
    }
]

def test_endpoint(test_case):
    """Test a single endpoint call"""
    print(f"\n{'='*80}")
    print(f"TEST: {test_case['name']}")
    print(f"{'='*80}")
    print(f"\nRequest:")
    print(json.dumps(test_case['payload'], indent=2))
    
    try:
        response = requests.post(API_URL, json=test_case['payload'], timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✓ Success! Status Code: {response.status_code}")
            print(f"\nResponse:")
            print(f"Description:\n{result['description']}")
        else:
            print(f"\n✗ Error! Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.RequestException as e:
        print(f"\n✗ Request failed: {str(e)}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")

def main():
    print("="*80)
    print("PRODUCT/SERVICE DESCRIPTION ENDPOINT TEST")
    print("="*80)
    print("\nMake sure the FastAPI server is running:")
    print("  uvicorn backend.app:app --reload")
    print("\nOr from backend directory:")
    print("  uvicorn app:app --reload")
    
    # Check if server is running
    try:
        health_check = requests.get("http://127.0.0.1:8000/", timeout=5)
        print(f"\n✓ Server is running!")
    except:
        print(f"\n✗ Server is not running. Please start it first.")
        return
    
    # Run all test cases
    for test_case in test_cases:
        test_endpoint(test_case)
        print("\n" + "-"*80)
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)

if __name__ == "__main__":
    main()

