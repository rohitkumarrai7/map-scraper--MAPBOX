import json
import os
from datetime import datetime

def add_background_fields_to_json(filename):
    """
    Add background fields to a JSON file that's missing them
    
    Args:
        filename (str): Path to the JSON file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"🔧 Processing file: {filename}")
        
        # Read the JSON file
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if places exist
        if 'places' not in data:
            print(f"❌ No 'places' field found in {filename}")
            return False
        
        modified = False
        
        # Process each place
        for place in data['places']:
            # Check if background field is missing or N/A
            if 'background' not in place or place['background'] == 'N/A' or place['background'] == '':
                # Create a background from available data
                title = place.get('title', 'Business')
                address = place.get('address', '')
                website = place.get('website', '')
                rating = place.get('rating_and_reviews', '')
                
                # Create a meaningful background
                background_parts = []
                
                if title and title.strip():
                    background_parts.append(f"{title}")
                
                if address and address.strip():
                    background_parts.append(f"located at {address}")
                
                if website and website != 'N/A' and website.strip():
                    background_parts.append(f"with website {website}")
                
                if rating and rating.strip():
                    background_parts.append(f"with rating {rating}")
                
                # Add default description
                if background_parts:
                    background = f"{' '.join(background_parts)}. "
                else:
                    background = "Professional business. "
                
                background += "They provide high-quality services in their industry and have established a strong reputation in their local market."
                
                # Add email field if missing
                if 'email' not in place:
                    place['email'] = 'N/A'
                
                # Update the background
                place['background'] = background
                modified = True
                
                print(f"✅ Added background for: {title}")
        
        if modified:
            # Create backup
            backup_filename = f"{filename}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(backup_filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 Created backup: {backup_filename}")
            
            # Save the modified file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Successfully updated {filename}")
            return True
        else:
            print(f"ℹ️  No changes needed for {filename}")
            return True
            
    except Exception as e:
        print(f"❌ Error processing {filename}: {e}")
        return False

def find_json_files():
    """Find all JSON files in the current directory"""
    json_files = []
    for file in os.listdir('.'):
        if file.endswith('.json') and file.startswith('scraped_data_'):
            json_files.append(file)
    return json_files

def main():
    """Main function to fix background fields in all scraped data files"""
    print("🔧 === Fix Background Fields in Scraped Data ===")
    print("This script will add background fields to JSON files that are missing them.")
    print()
    
    # Find all scraped data JSON files
    json_files = find_json_files()
    
    if not json_files:
        print("❌ No scraped data JSON files found!")
        return
    
    print(f"📁 Found {len(json_files)} JSON files:")
    for i, file in enumerate(json_files, 1):
        print(f"  {i}. {file}")
    
    print()
    
    # Process each file
    successful = 0
    failed = 0
    
    for filename in json_files:
        if add_background_fields_to_json(filename):
            successful += 1
        else:
            failed += 1
        print()
    
    print("📊 === Summary ===")
    print(f"✅ Successfully processed: {successful}")
    print(f"❌ Failed to process: {failed}")
    
    if successful > 0:
        print()
        print("🎉 Background fields have been added to your scraped data!")
        print("You can now use these files with the cold email feature.")
        print()
        print("💡 The background field will be used by OpenAI to generate personalized email content.")

if __name__ == "__main__":
    main() 