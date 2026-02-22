"""
Navigation Test for CryptexQ
Tests that all routes are accessible and pages render correctly
"""

from app import app
import pytest

def test_all_routes():
    """Test that all routes return 200 status code"""
    
    client = app.test_client()
    
    routes_to_test = [
        ('/', 'index_page'),
        ('/home', 'home_page'),
        ('/talkroom', 'talkroom_page'),
        ('/demo', 'demo_page'),
        ('/about', 'about_page'),
        ('/team', 'team_page'),
        ('/faq', 'faq_page'),
        ('/contact', 'contact_page'),
        ('/term', 'terms_page'),
        ('/login', 'login_route'),
        ('/signup', 'signup_route'),
        ('/logout', 'logout_page'),
        ('/forgetpg', 'forgetpg_page'),
        ('/profile', 'profile_page'),
        ('/replay-protection', 'replay_protection_page'),
        ('/secure-msg', 'secure_msg_page'),
    ]
    
    print("\n" + "="*60)
    print("TESTING ALL NAVIGATION ROUTES")
    print("="*60)
    
    all_passed = True
    
    for route, name in routes_to_test:
        response = client.get(route)
        status = "✅ PASS" if response.status_code == 200 else "❌ FAIL"
        
        if response.status_code != 200:
            all_passed = False
            
        print(f"{status} | {route:25} | {name:30} | Status: {response.status_code}")
    
    print("="*60)
    
    if all_passed:
        print("✅ ALL ROUTES WORKING! Navigation is fully connected.")
    else:
        print("❌ Some routes failed. Check the output above.")
    
    print("="*60 + "\n")
    
    return all_passed


if __name__ == "__main__":
    with app.app_context():
        success = test_all_routes()
        
    if success:
        print("🎉 All pages are connected and working properly!")
    else:
        print("⚠️  Some pages need fixing.")
