"""
Debug script to test driver initialization
Run this to see detailed error messages
"""
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from auth_service import auth_service

print("=" * 70)
print("TESTING DRIVER INITIALIZATION")
print("=" * 70)

print("\n[TEST 1] Calling open_login_page()...")
success, message = auth_service.open_login_page()

print(f"\nResult: {'✓ SUCCESS' if success else '✗ FAILED'}")
print(f"Message: {message}")

if success:
    print("\n[TEST 2] Browser should be open now. Check if Chrome window appeared.")
    input("Press Enter to close browser and exit...")
    auth_service.close()
    print("✓ Browser closed")
else:
    print("\n[DEBUG] Error details above ↑")
    print("\nPossible causes:")
    print("1. ChromeDriver version mismatch with installed Chrome")
    print("2. Stale driver process still running")
    print("3. Chrome binary not found")
    
print("\n" + "=" * 70)
