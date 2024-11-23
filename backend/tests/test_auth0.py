import os
import json
import requests
from dotenv import load_dotenv
from typing import Dict, Optional
import jwt
from jwt.algorithms import RSAAlgorithm


class Auth0Tester:
    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Auth0 configuration
        self.domain = os.getenv('AUTH0_DOMAIN')
        self.audience = os.getenv('AUTH0_AUDIENCE')
        self.client_id = os.getenv('AUTH0_CLIENT_ID')
        self.client_secret = os.getenv('AUTH0_CLIENT_SECRET')

        # Verify all required env vars are present
        self._verify_env_vars()

        # URLs
        self.oauth_url = f"https://{self.domain}/oauth/token"
        self.jwks_url = f"https://{self.domain}/.well-known/jwks.json"

        # Store test results
        self.test_results = []

    def _verify_env_vars(self) -> None:
        """Verify all required environment variables are set"""
        required_vars = {
            'AUTH0_DOMAIN': self.domain,
            'AUTH0_AUDIENCE': self.audience,
            'AUTH0_CLIENT_ID': self.client_id,
            'AUTH0_CLIENT_SECRET': self.client_secret
        }

        missing_vars = [var for var, value in required_vars.items() if not value]

        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

    def _add_test_result(self, test_name: str, success: bool, message: str) -> None:
        """Add a test result to the results list"""
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })

    def get_access_token(self) -> Optional[str]:
        """Attempt to get an access token from Auth0"""
        try:
            payload = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'audience': self.audience,
                'grant_type': 'client_credentials'
            }

            response = requests.post(self.oauth_url, json=payload)
            response.raise_for_status()

            token = response.json().get('access_token')
            if token:
                self._add_test_result(
                    "Get Access Token",
                    True,
                    "Successfully obtained access token"
                )
                return token
            else:
                self._add_test_result(
                    "Get Access Token",
                    False,
                    "No access token in response"
                )
                return None

        except requests.exceptions.RequestException as e:
            self._add_test_result(
                "Get Access Token",
                False,
                f"Failed to get access token: {str(e)}"
            )
            return None

    def verify_token(self, token: str) -> bool:
        """Verify the JWT token using Auth0's JWKS"""
        try:
            # Get the JWKS
            jwks_response = requests.get(self.jwks_url)
            jwks_response.raise_for_status()
            jwks = jwks_response.json()

            # Decode header without verification
            header = jwt.get_unverified_header(token)

            # Find the key in JWKS
            key = None
            for jwk in jwks['keys']:
                if jwk['kid'] == header['kid']:
                    key = RSAAlgorithm.from_jwk(json.dumps(jwk))
                    break

            if not key:
                self._add_test_result(
                    "Verify Token",
                    False,
                    "Could not find appropriate key in JWKS"
                )
                return False

            # Verify the token
            decoded = jwt.decode(
                token,
                key,
                algorithms=['RS256'],
                audience=self.audience,
                issuer=f"https://{self.domain}/"
            )

            self._add_test_result(
                "Verify Token",
                True,
                f"Successfully verified token. Payload: {json.dumps(decoded, indent=2)}"
            )
            return True

        except Exception as e:
            self._add_test_result(
                "Verify Token",
                False,
                f"Failed to verify token: {str(e)}"
            )
            return False

    def test_configuration(self) -> Dict:
        """Run all configuration tests"""
        print("\nTesting Auth0 Configuration...")
        print("-" * 50)

        # Test 1: Get Access Token
        token = self.get_access_token()
        if not token:
            print("\n❌ Failed to get access token. Stopping tests.")
            return {"success": False, "results": self.test_results}

        print("✅ Successfully obtained access token")

        # Test 2: Verify Token
        if not self.verify_token(token):
            print("\n❌ Failed to verify token. Stopping tests.")
            return {"success": False, "results": self.test_results}

        print("✅ Successfully verified token")

        print("\nAll tests completed successfully! 🎉")
        return {"success": True, "results": self.test_results}


def main():
    try:
        tester = Auth0Tester()
        results = tester.test_configuration()

        print("\nDetailed Test Results:")
        print("-" * 50)
        for result in results['results']:
            status = "✅" if result['success'] else "❌"
            print(f"\n{status} {result['test']}:")
            print(f"   {result['message']}")

    except Exception as e:
        print(f"\n❌ Setup Error: {str(e)}")
        print("\nPlease verify your environment variables and Auth0 configuration.")


if __name__ == "__main__":
    main()