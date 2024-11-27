import requests
import json
import re

# Read the JWT token from file
with open('jwt_token.json') as f:
    token_data = json.load(f)
    jwt_token = token_data['jwtToken']

headers = {
    'Authorization': f'Bearer {jwt_token}',
    'Accept': '*/*',
}

init_url = 'https://terracore.herokuapp.com/api-docs/swagger-ui-init.js'
response = requests.get(init_url, headers=headers)

if response.status_code == 200:
    # Extract the swagger doc from the JavaScript
    content = response.text
    
    # Find the swaggerDoc object
    match = re.search(r'"swaggerDoc":\s*({[\s\S]*?})(?=,\s*"customOptions"|$)', content)
    
    if match:
        try:
            # Clean up the matched string and parse it as JSON
            swagger_doc_str = match.group(1)
            
            # Clean up newlines and escape sequences in the string
            swagger_doc_str = swagger_doc_str.replace('\n', '\\n')
            # Remove any existing escaped quotes and then re-escape them
            swagger_doc_str = swagger_doc_str.replace('\\"', '"').replace('"', '\\"')
            # Wrap the entire string in quotes
            swagger_doc_str = f'"{swagger_doc_str}"'
            
            # Unescape the string using json.loads
            swagger_doc_str = json.loads(swagger_doc_str)
            # Now parse the actual JSON
            swagger_doc = json.loads(swagger_doc_str)
            
            # Save to file
            with open('api-docs.json', 'w', encoding='utf-8') as f:
                json.dump(swagger_doc, f, indent=2, ensure_ascii=False)
            
            print("Successfully extracted and saved the OpenAPI specification to api-docs.json")
            print("\nAPI Info:")
            print(f"Title: {swagger_doc.get('info', {}).get('title')}")
            print(f"Version: {swagger_doc.get('info', {}).get('version')}")
            description = swagger_doc.get('info', {}).get('description', '')
            if description:
                print(f"Description: {description[:100]}...")
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print("Let's try an alternative parsing approach...")
            
            try:
                # Alternative approach: manual regex extraction
                info_match = re.search(r'{[\s\S]*?"swagger":\s*"([^"]+)"[\s\S]*?"info":\s*{([\s\S]*?)}', content)
                if info_match:
                    print("\nExtracted API Info (via regex):")
                    print(f"Swagger Version: {info_match.group(1)}")
                    info_content = info_match.group(2)
                    title_match = re.search(r'"title":\s*"([^"]+)"', info_content)
                    version_match = re.search(r'"version":\s*"([^"]+)"', info_content)
                    if title_match:
                        print(f"Title: {title_match.group(1)}")
                    if version_match:
                        print(f"Version: {version_match.group(1)}")
                    
                    # Save raw content for manual inspection
                    with open('api-docs-raw.txt', 'w', encoding='utf-8') as f:
                        f.write(swagger_doc_str)
                    print("\nRaw content saved to api-docs-raw.txt for manual inspection")
            except Exception as e:
                print(f"Alternative parsing also failed: {e}")
    else:
        print("Could not find swaggerDoc in the initialization file")
        print("Raw content received:")
        print(content[:500])
else:
    print(f"Failed to fetch init file: {response.status_code}")
