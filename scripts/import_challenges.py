import json
import argparse
import requests
import re

def extract_function_name(function_signature):
    """Extract function name from the function signature."""
    match = re.search(r'def\s+(\w+)', function_signature)
    if match:
        return match.group(1)
    return None

def create_challenge(challenge_data, api_url, token):
    """Create a challenge using the API."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Extract or generate title
    title = challenge_data.get('title')
    if not title:
        function_name = extract_function_name(challenge_data['function_signature'])
        title = function_name if function_name else "Untitled Challenge"

    # Prepare challenge data
    challenge = {
        "title": title,
        "description": challenge_data['description'],
        "function_signature": challenge_data['function_signature'],
        "theorem_signature": challenge_data['theorem_signature'] if challenge_data['theorem_signature'] else '',
        "theorem2_signature": challenge_data.get('theorem2_signature')
    }

    try:
        response = requests.post(f"{api_url}/api/challenges/", json=challenge, headers=headers)
        response.raise_for_status()
        print(f"Successfully created challenge: {title}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to create challenge {title}: {str(e)}")
        if hasattr(e.response, 'text'):
            print(f"Error details: {e.response.text}")
        return None

def login(api_url, email, password):
    """Login and get access token."""
    try:
        response = requests.post(
            f"{api_url}/api/auth/login",
            data={"username": email, "password": password}
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.exceptions.RequestException as e:
        print(f"Failed to login: {str(e)}")
        if hasattr(e.response, 'text'):
            print(f"Error details: {e.response.text}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Import challenges from a JSONL file')
    parser.add_argument('file', help='Path to the JSONL file containing challenges')
    parser.add_argument('--api-url', default='http://localhost:8000', 
                       help='Base URL of the API (default: http://localhost:8000)')
    parser.add_argument('--email', required=True, help='Email for authentication')
    parser.add_argument('--password', required=True, help='Password for authentication')
    
    args = parser.parse_args()

    # Login and get token
    token = login(args.api_url, args.email, args.password)
    if not token:
        print("Failed to authenticate. Exiting.")
        return

    # Read and process challenges
    successful = 0
    failed = 0

    try:
        with open(args.file, 'r') as f:
            for line_number, line in enumerate(f, 1):
                try:
                    challenge_data = json.loads(line.strip())
                    result = create_challenge(challenge_data, args.api_url, token)
                    if result:
                        successful += 1
                    else:
                        failed += 1
                except json.JSONDecodeError as e:
                    print(f"Error parsing line {line_number}: {str(e)}")
                    failed += 1
                except Exception as e:
                    print(f"Error processing line {line_number}: {str(e)}")
                    failed += 1

    except FileNotFoundError:
        print(f"File not found: {args.file}")
        return

    print(f"\nImport completed:")
    print(f"Successfully imported: {successful}")
    print(f"Failed: {failed}")

if __name__ == "__main__":
    main()

