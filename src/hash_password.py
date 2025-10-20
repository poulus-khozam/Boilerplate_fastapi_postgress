import sys
import os

# This ensures that the script can find the 'core' module
# by adding its parent directory ('/app/src') to the system path.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.security import get_password_hash

# This script takes one command-line argument: the password to hash.
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python hash_password.py <your_password_here>")
        sys.exit(1)
    
    plain_password = sys.argv[1]
    hashed_password = get_password_hash(plain_password)
    
    print("Plain Password:", plain_password)
    print("Hashed Password:", hashed_password)
    print("\n✅ You can now use this hashed password in your database.")
