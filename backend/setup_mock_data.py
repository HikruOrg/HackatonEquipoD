# Sample Mock Data Setup Script
# This script helps you create sample directories and explains the expected structure

import os
from pathlib import Path

def create_mock_data_structure():
    """Create the expected directory structure for local testing"""
    
    base_dir = Path("mock_data")
    base_dir.mkdir(exist_ok=True)
    
    # Sample users
    users = ["user1", "user2", "user3", "user4", "user5"]
    
    for user in users:
        user_dir = base_dir / user
        user_dir.mkdir(exist_ok=True)
        
        # Create placeholder text files to indicate where images should go
        readme_file = user_dir / "README.txt"
        with open(readme_file, "w") as f:
            f.write(f"""
Place your test images for {user} in this folder.

Supported formats:
- .jpg
- .jpeg
- .png
- .bmp
- .gif

Example structure:
{user}/
├── photo1.jpg
├── vacation.png
├── family.jpeg
└── pet.jpg

For meaningful results, add at least 20+ images per user folder.
Make sure you have diverse content (people, animals, objects, landscapes, etc.)
to test the categorization effectively.
""")
        
        print(f"✅ Created directory structure for {user}")
    
    print(f"\n🎯 Mock data structure created in '{base_dir}'")
    print("\n📁 Next steps:")
    print("1. Add real images to each user folder")
    print("2. Remove the README.txt files")
    print("3. Set USE_LOCAL_STORAGE=true in .env")
    print("4. Start the API and test!")

if __name__ == "__main__":
    create_mock_data_structure()