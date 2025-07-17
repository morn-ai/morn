#!/usr/bin/env python3
"""
Test script to verify authentication modes work correctly.
Run this script to test both JWT and no-auth modes.
"""

import os
import requests
import json
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USERNAME = "test_user"
TEST_PASSWORD = "test_password"

def test_jwt_mode():
    """Test JWT authentication mode"""
    print("=== Testing JWT Mode ===")
    
    # Set environment variable
    os.environ["MORN_AUTH_MODE"] = "jwt"
    os.environ["MORN_ADMIN_USERNAME"] = "admin"
    os.environ["MORN_ADMIN_PASSWORD"] = "admin123"
    os.environ["JWT_SECRET_KEY"] = "test-secret-key"
    
    # Test 1: Try to access protected endpoint without token
    print("1. Testing access without token...")
    try:
        response = requests.get(f"{BASE_URL}/me")
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✓ Correctly rejected without token")
        else:
            print("   ✗ Should have been rejected")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Login with correct credentials
    print("2. Testing login with correct credentials...")
    try:
        response = requests.post(f"{BASE_URL}/api/v1/login", json={
            "username": "admin",
            "password": "admin123"
        })
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print("   ✓ Login successful")
            
            # Test 3: Access protected endpoint with token
            print("3. Testing access with valid token...")
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}/me", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                user_data = response.json()
                print(f"   ✓ Access granted, username: {user_data.get('username')}")
            else:
                print("   ✗ Should have been granted access")
        else:
            print("   ✗ Login failed")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Login with wrong credentials
    print("4. Testing login with wrong credentials...")
    try:
        response = requests.post(f"{BASE_URL}/api/v1/login", json={
            "username": "wrong_user",
            "password": "wrong_password"
        })
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✓ Correctly rejected wrong credentials")
        else:
            print("   ✗ Should have been rejected")
    except Exception as e:
        print(f"   Error: {e}")

def test_no_auth_mode():
    """Test no authentication mode"""
    print("\n=== Testing No Auth Mode ===")
    
    # Set environment variable
    os.environ["MORN_AUTH_MODE"] = "none"
    
    # Test 1: Access protected endpoint without token
    print("1. Testing access without token...")
    try:
        response = requests.get(f"{BASE_URL}/me")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✓ Access granted, username: {user_data.get('username')}")
        else:
            print("   ✗ Should have been granted access")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Login with any credentials
    print("2. Testing login with any credentials...")
    try:
        response = requests.post(f"{BASE_URL}/api/v1/login", json={
            "username": "any_user",
            "password": "any_password"
        })
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print("   ✓ Login successful with any credentials")
            
            # Test 3: Access protected endpoint with token
            print("3. Testing access with token...")
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}/me", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                user_data = response.json()
                print(f"   ✓ Access granted, username: {user_data.get('username')}")
            else:
                print("   ✗ Should have been granted access")
        else:
            print("   ✗ Login should have succeeded")
    except Exception as e:
        print(f"   Error: {e}")

def test_chat_api():
    """Test chat API with different auth modes"""
    print("\n=== Testing Chat API ===")
    
    # Test JWT mode
    print("1. Testing chat API in JWT mode...")
    os.environ["MORN_AUTH_MODE"] = "jwt"
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/chat/completions", json={
            "messages": [{"role": "user", "content": "Hello"}],
            "stream": False
        })
        print(f"   Status without token: {response.status_code}")
        if response.status_code == 401:
            print("   ✓ Correctly rejected without token")
        else:
            print("   ✗ Should have been rejected")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test no auth mode
    print("2. Testing chat API in no auth mode...")
    os.environ["MORN_AUTH_MODE"] = "none"
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/chat/completions", json={
            "messages": [{"role": "user", "content": "Hello"}],
            "stream": False
        })
        print(f"   Status without token: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Access granted without token")
        else:
            print("   ✗ Should have been granted access")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    print("Authentication Mode Test Script")
    print("Make sure the server is running on http://localhost:8000")
    print("=" * 50)
    
    try:
        test_jwt_mode()
        test_no_auth_mode()
        test_chat_api()
        print("\n" + "=" * 50)
        print("Test completed!")
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed with error: {e}") 
