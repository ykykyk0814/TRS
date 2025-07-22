# This script is NOT a pytest test file. It is for manual/CI verification only.
# pytest: skip-file

# !/usr/bin/env python3
"""
Endpoint verification script for Travel Recommendation System API.

This script:
1. Registers a test user
2. Authenticates and gets JWT token
3. Tests all protected endpoints
4. Cleans up test data

Usage:
    python tests/verify_endpoints.py [--base-url http://localhost:8000]
"""

import argparse
import asyncio
import sys
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional

import httpx


class APIVerifier:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.api_base = f"{self.base_url}/api"
        self.client = httpx.AsyncClient(timeout=30.0)
        self.auth_token: Optional[str] = None
        self.test_user_id: Optional[str] = None
        self.test_ticket_id: Optional[int] = None
        self.test_preference_id: Optional[int] = None

        # Test user data
        self.test_email = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
        self.test_password = "TestPassword123!"

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get headers with auth token if available."""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers

    async def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> httpx.Response:
        """Make HTTP request with proper error handling."""
        url = f"{self.api_base}{endpoint}"
        try:
            response = await self.client.request(method, url, **kwargs)
            return response
        except Exception as e:
            print(f"❌ Request failed for {method} {endpoint}: {e}")
            raise

    def _print_result(self, test_name: str, success: bool, details: str = ""):
        """Print formatted test result."""
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")

    async def test_health_endpoints(self) -> bool:
        """Test health check endpoints."""
        print("\n🔍 Testing Health Endpoints...")

        try:
            # Test health endpoint
            response = await self._make_request("GET", "/health")
            health_ok = response.status_code == 200
            self._print_result(
                "Health check", health_ok, f"Status: {response.status_code}"
            )

            # Test info endpoint
            response = await self._make_request("GET", "/info")
            info_ok = response.status_code == 200
            self._print_result("API info", info_ok, f"Status: {response.status_code}")

            return health_ok and info_ok
        except Exception as e:
            self._print_result("Health endpoints", False, str(e))
            return False

    async def test_user_registration(self) -> bool:
        """Test user registration."""
        print("\n🔍 Testing User Registration...")

        try:
            user_data = {
                "email": self.test_email,
                "password": self.test_password,
                "full_name": "Test User",
            }

            response = await self._make_request(
                "POST",
                "/auth/register",
                headers={"Content-Type": "application/json"},
                json=user_data,
            )

            success = response.status_code == 201
            if success:
                user_info = response.json()
                self.test_user_id = user_info.get("id")
                self._print_result(
                    "User registration", True, f"User ID: {self.test_user_id}"
                )
            else:
                self._print_result(
                    "User registration",
                    False,
                    f"Status: {response.status_code}, Body: {response.text}",
                )

            return success
        except Exception as e:
            self._print_result("User registration", False, str(e))
            return False

    async def test_authentication(self) -> bool:
        """Test JWT authentication."""
        print("\n🔍 Testing JWT Authentication...")

        try:
            # Login to get JWT token
            login_data = {
                "username": self.test_email,  # FastAPI-Users uses 'username' field for email
                "password": self.test_password,
            }

            response = await self._make_request(
                "POST",
                "/auth/jwt/login",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data=login_data,
            )

            if response.status_code in [200, 204]:
                # Check if we got a token in cookies or response
                if "auth" in response.cookies:
                    # Cookie-based auth
                    self.auth_token = None  # Will use cookies
                    self.client.cookies = response.cookies
                    self._print_result(
                        "JWT Authentication", True, "Using cookie-based auth"
                    )
                    return True
                elif response.status_code == 200:
                    # Try to get token from response body
                    try:
                        token_data = response.json()
                        self.auth_token = token_data.get("access_token")
                        if self.auth_token:
                            self._print_result(
                                "JWT Authentication", True, "Using bearer token auth"
                            )
                            return True
                        else:
                            self._print_result(
                                "JWT Authentication", False, "No token in response"
                            )
                            return False
                    except Exception:
                        self._print_result(
                            "JWT Authentication",
                            False,
                            "Could not parse token response",
                        )
                        return False
                elif response.status_code == 204:
                    # 204 with no cookies means something went wrong
                    self._print_result(
                        "JWT Authentication", False, "Got 204 but no auth cookie found"
                    )
                    return False

                return True
            else:
                self._print_result(
                    "JWT Authentication",
                    False,
                    f"Status: {response.status_code}, Body: {response.text}",
                )
                return False

        except Exception as e:
            self._print_result("JWT Authentication", False, str(e))
            return False

    async def test_protected_user_endpoint(self) -> bool:
        """Test accessing protected user endpoint."""
        print("\n🔍 Testing Protected User Endpoint...")

        try:
            response = await self._make_request(
                "GET", "/auth/users/me", headers=self._get_auth_headers()
            )

            success = response.status_code == 200
            if success:
                user_data = response.json()
                self._print_result(
                    "Get current user profile", True, f"Email: {user_data.get('email')}"
                )
            else:
                self._print_result(
                    "Get current user profile", False, f"Status: {response.status_code}"
                )

            return success
        except Exception as e:
            self._print_result("Get current user profile", False, str(e))
            return False

    async def test_preferences_endpoints(self) -> bool:
        """Test preferences CRUD operations."""
        print("\n🔍 Testing Preferences Endpoints...")
        results = []

        try:
            # Create preference
            preference_data = {
                "user_id": self.test_user_id,
                "prefers_email": True,
                "prefers_sms": False,
            }

            response = await self._make_request(
                "POST",
                "/preferences/",
                headers=self._get_auth_headers(),
                json=preference_data,
            )

            create_success = response.status_code == 200
            if create_success:
                pref_data = response.json()
                self.test_preference_id = pref_data.get("id")
                self._print_result(
                    "Create preference",
                    True,
                    f"Preference ID: {self.test_preference_id}",
                )
            else:
                self._print_result(
                    "Create preference", False, f"Status: {response.status_code}"
                )
            results.append(create_success)

            if create_success:
                # Get preference
                response = await self._make_request(
                    "GET",
                    f"/preferences/{self.test_preference_id}",
                    headers=self._get_auth_headers(),
                )
                get_success = response.status_code == 200
                self._print_result(
                    "Get preference", get_success, f"Status: {response.status_code}"
                )
                results.append(get_success)

                # Update preference
                update_data = {"prefers_sms": True}
                response = await self._make_request(
                    "PUT",
                    f"/preferences/{self.test_preference_id}",
                    headers=self._get_auth_headers(),
                    json=update_data,
                )
                update_success = response.status_code == 200
                self._print_result(
                    "Update preference",
                    update_success,
                    f"Status: {response.status_code}",
                )
                results.append(update_success)

            return all(results)
        except Exception as e:
            self._print_result("Preferences endpoints", False, str(e))
            return False

    async def test_tickets_endpoints(self) -> bool:
        """Test tickets CRUD operations."""
        print("\n🔍 Testing Tickets Endpoints...")
        results = []

        try:
            # Create ticket
            ticket_data = {
                "user_id": self.test_user_id,
                "origin": "New York",
                "destination": "Los Angeles",
                "departure_time": (datetime.now() + timedelta(days=30)).isoformat(),
                "arrival_time": (
                    datetime.now() + timedelta(days=30, hours=5)
                ).isoformat(),
                "seat_number": "12A",
                "notes": "Test ticket",
            }

            response = await self._make_request(
                "POST", "/tickets/", headers=self._get_auth_headers(), json=ticket_data
            )

            create_success = response.status_code == 200
            if create_success:
                ticket_resp = response.json()
                self.test_ticket_id = ticket_resp.get("id")
                self._print_result(
                    "Create ticket", True, f"Ticket ID: {self.test_ticket_id}"
                )
            else:
                self._print_result(
                    "Create ticket", False, f"Status: {response.status_code}"
                )
            results.append(create_success)

            if create_success:
                # Get ticket
                response = await self._make_request(
                    "GET",
                    f"/tickets/{self.test_ticket_id}",
                    headers=self._get_auth_headers(),
                )
                get_success = response.status_code == 200
                self._print_result(
                    "Get ticket", get_success, f"Status: {response.status_code}"
                )
                results.append(get_success)

                # Get all tickets
                response = await self._make_request(
                    "GET", "/tickets/", headers=self._get_auth_headers()
                )
                list_success = response.status_code == 200
                self._print_result(
                    "List tickets", list_success, f"Status: {response.status_code}"
                )
                results.append(list_success)

                # Update ticket
                update_data = {"seat_number": "15B", "notes": "Updated test ticket"}
                response = await self._make_request(
                    "PUT",
                    f"/tickets/{self.test_ticket_id}",
                    headers=self._get_auth_headers(),
                    json=update_data,
                )
                update_success = response.status_code == 200
                self._print_result(
                    "Update ticket", update_success, f"Status: {response.status_code}"
                )
                results.append(update_success)

            return all(results)
        except Exception as e:
            self._print_result("Tickets endpoints", False, str(e))
            return False

    async def cleanup_test_data(self) -> bool:
        """Clean up test data."""
        print("\n🧹 Cleaning up test data...")
        results = []

        try:
            # Delete ticket
            if self.test_ticket_id:
                response = await self._make_request(
                    "DELETE",
                    f"/tickets/{self.test_ticket_id}",
                    headers=self._get_auth_headers(),
                )
                ticket_cleanup = response.status_code == 200
                self._print_result(
                    "Delete test ticket",
                    ticket_cleanup,
                    f"Status: {response.status_code}",
                )
                results.append(ticket_cleanup)

            # Delete preference
            if self.test_preference_id:
                response = await self._make_request(
                    "DELETE",
                    f"/preferences/{self.test_preference_id}",
                    headers=self._get_auth_headers(),
                )
                pref_cleanup = response.status_code == 200
                self._print_result(
                    "Delete test preference",
                    pref_cleanup,
                    f"Status: {response.status_code}",
                )
                results.append(pref_cleanup)

            # Note: We don't delete the user as FastAPI-Users doesn't provide a delete endpoint by default

            return all(results) if results else True
        except Exception as e:
            self._print_result("Cleanup", False, str(e))
            return False

    async def run_verification(self) -> bool:
        """Run all verification tests."""
        print(f"🚀 Starting API verification for {self.base_url}")

        # Run tests in order
        tests = [
            ("Health Check", self.test_health_endpoints),
            ("User Registration", self.test_user_registration),
            ("JWT Authentication", self.test_authentication),
            ("Protected Endpoints", self.test_protected_user_endpoint),
            ("Preferences CRUD", self.test_preferences_endpoints),
            ("Tickets CRUD", self.test_tickets_endpoints),
        ]

        results = []
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results.append(result)
                if not result:
                    print(f"❌ {test_name} failed - stopping verification")
                    break
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results.append(False)
                break

        # Always try cleanup
        await self.cleanup_test_data()

        # Summary
        print("\n📊 Verification Summary:")
        print(f"   Total tests: {len(tests)}")
        print(f"   Passed: {sum(results)}")
        print(f"   Failed: {len(results) - sum(results)}")

        overall_success = all(results)
        status = "✅ All tests passed!" if overall_success else "❌ Some tests failed!"
        print(f"   {status}")

        return overall_success


async def main():
    parser = argparse.ArgumentParser(
        description="Verify Travel Recommendation System API endpoints"
    )
    parser.add_argument(
        "--base-url", default="http://localhost:8000", help="Base URL of the API"
    )
    args = parser.parse_args()

    async with APIVerifier(args.base_url) as verifier:
        success = await verifier.run_verification()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
