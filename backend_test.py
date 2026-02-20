import requests
import sys
from datetime import datetime
import json

class SquarerootzAPITester:
    def __init__(self, base_url="https://ai-learn-hub-150.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session_token = "test_session_1771274914292"
        self.test_user_id = "test-user-1771274914292"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def get_headers(self, include_auth=False):
        """Get headers for API requests"""
        headers = {'Content-Type': 'application/json'}
        if include_auth:
            headers['Authorization'] = f'Bearer {self.session_token}'
        return headers

    def run_test(self, name, method, endpoint, expected_status, data=None, include_auth=False, timeout=30):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = self.get_headers(include_auth)
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            
            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Response: {response.text[:200]}")
                
                self.failed_tests.append({
                    "test_name": name,
                    "endpoint": endpoint,
                    "expected_status": expected_status,
                    "actual_status": response.status_code,
                    "error": response.text[:200] if response.text else "No response body"
                })
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Exception: {str(e)}")
            self.failed_tests.append({
                "test_name": name,
                "endpoint": endpoint,
                "expected_status": expected_status,
                "actual_status": "ERROR",
                "error": str(e)
            })
            return False, {}

    def test_public_endpoints(self):
        """Test all public endpoints that don't require authentication"""
        print("\n" + "="*50)
        print("TESTING PUBLIC ENDPOINTS")
        print("="*50)
        
        # Test root endpoint
        success, data = self.run_test("API Root", "GET", "", 200)
        
        # Test get all courses
        success, courses = self.run_test("Get All Courses", "GET", "courses", 200)
        if success and courses:
            print(f"   Found {len(courses)} courses")
            if len(courses) != 10:
                print(f"   ⚠️  Expected 10 courses, got {len(courses)}")
            
            # Check pricing is in lakh range (100000-300000)
            price_issues = []
            for course in courses:
                price = course.get('price', 0)
                if price < 100000 or price > 300000:
                    price_issues.append(f"{course.get('title', 'Unknown')}: ₹{price}")
            
            if price_issues:
                print(f"   ⚠️  Courses with prices outside lakh range (1-3 lakh):")
                for issue in price_issues:
                    print(f"      - {issue}")
            else:
                print(f"   ✅ All course prices in lakh range (₹1,00,000 - ₹3,00,000)")
        
        # Test course categories
        success, categories = self.run_test("Get Categories", "GET", "categories", 200)
        if success and categories:
            print(f"   Found categories: {categories}")
        
        # Test specific course detail
        success, course_detail = self.run_test("Get Course Detail (ML)", "GET", "courses/machine-learning", 200)
        if success and course_detail:
            print(f"   Course: {course_detail.get('title', 'No title')}")
            required_fields = ['course_id', 'title', 'syllabus', 'why_select', 'price', 'instructor']
            for field in required_fields:
                if field not in course_detail:
                    print(f"   ⚠️  Missing required field: {field}")
        
        # Test invalid course
        success, _ = self.run_test("Get Invalid Course", "GET", "courses/non-existent", 404)
        
        # Test contact form submission
        contact_data = {
            "name": "Test User",
            "email": "test@example.com", 
            "subject": "Test Subject",
            "message": "This is a test message"
        }
        success, _ = self.run_test("Submit Contact Form", "POST", "contact", 200, data=contact_data)

    def test_auth_endpoints(self):
        """Test authentication-related endpoints"""
        print("\n" + "="*50)
        print("TESTING AUTH ENDPOINTS")
        print("="*50)
        
        # Test get current user with valid session
        success, user_data = self.run_test("Get Current User", "GET", "auth/me", 200, include_auth=True)
        if success and user_data:
            print(f"   User: {user_data.get('name', 'No name')} ({user_data.get('email', 'No email')})")
            if user_data.get('user_id') != self.test_user_id:
                print(f"   ⚠️  Expected user_id {self.test_user_id}, got {user_data.get('user_id')}")
        
        # Test auth without session token
        success, _ = self.run_test("Get Current User (No Auth)", "GET", "auth/me", 401)

    def test_order_enrollment_flow(self):
        """Test order creation and enrollment flow"""
        print("\n" + "="*50)
        print("TESTING ORDER & ENROLLMENT FLOW")
        print("="*50)
        
        # Test create order
        order_data = {"course_id": "ml-101"}
        success, order_response = self.run_test("Create Order", "POST", "orders/create", 200, data=order_data, include_auth=True)
        
        order_id = None
        if success and order_response:
            order_id = order_response.get('order_id')
            print(f"   Order ID: {order_id}")
            print(f"   Amount: ₹{order_response.get('amount', 'N/A')}")
            print(f"   Demo Mode: {order_response.get('demo_mode', False)}")
            
            if not order_response.get('demo_mode'):
                print("   ⚠️  Expected demo mode to be True (no Razorpay keys)")
        
        # Test payment verification (demo mode)
        if order_id:
            verify_data = {
                "order_id": order_id,
                "payment_id": f"demo_pay_{int(datetime.now().timestamp())}",
                "signature": ""
            }
            success, verify_response = self.run_test("Verify Payment (Demo)", "POST", "orders/verify", 200, data=verify_data, include_auth=True)
            if success and verify_response:
                print(f"   Enrollment ID: {verify_response.get('enrollment_id', 'N/A')}")
        
        # Test get enrollments
        success, enrollments = self.run_test("Get User Enrollments", "GET", "enrollments", 200, include_auth=True)
        if success and enrollments:
            print(f"   Found {len(enrollments)} enrollments")
            for enrollment in enrollments:
                print(f"   - {enrollment.get('course_title', 'No title')} (Status: {enrollment.get('status', 'N/A')})")

    def test_invalid_auth_endpoints(self):
        """Test auth endpoints without proper authentication"""
        print("\n" + "="*50)
        print("TESTING INVALID AUTH SCENARIOS")
        print("="*50)
        
        # Test protected endpoints without auth
        success, _ = self.run_test("Create Order (No Auth)", "POST", "orders/create", 401, data={"course_id": "ml-101"})
        success, _ = self.run_test("Get Enrollments (No Auth)", "GET", "enrollments", 401)
        
        # Test with invalid course_id
        invalid_order_data = {"course_id": "invalid-course"}
        success, _ = self.run_test("Create Order (Invalid Course)", "POST", "orders/create", 404, data=invalid_order_data, include_auth=True)

    def print_summary(self):
        """Print test results summary"""
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {len(self.failed_tests)}")
        print(f"Success Rate: {(self.tests_passed / self.tests_run * 100):.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"- {test['test_name']}: Expected {test['expected_status']}, got {test['actual_status']}")
                print(f"  Endpoint: {test['endpoint']}")
                print(f"  Error: {test['error'][:100]}...")
        
        return len(self.failed_tests) == 0

def main():
    """Main test runner"""
    print("Squarerootz AI EdTech Platform - Backend API Testing")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = SquarerootzAPITester()
    
    # Run all test suites
    tester.test_public_endpoints()
    tester.test_auth_endpoints()
    tester.test_order_enrollment_flow()
    tester.test_invalid_auth_endpoints()
    
    # Print summary and return appropriate exit code
    all_passed = tester.print_summary()
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())