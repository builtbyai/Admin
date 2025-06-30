import os
from pathlib import Path

# Define the folder path
folder_path = r"S:\DriveSyncFiles\WORK MAIN\GOLDEN WEBSITE\WARRANTY AND LOGO"

# Define the rename mappings
rename_mappings = {
    "04d16ecf-4c00-40e1-80f9-a4bcaf84e1ab.png": "licensed_roofing_contractors_association_of_texas_logo.png",
    "0006_www_malarkeyroofing_com_75972332.jpg": "malarkey_roofing_products_when_it_matters.jpg",
    "0017_www_tamko_com_17272807.jpg": "americas_shingle_company_logo_established_1944.jpg",
    "0028_www_tamko_com_17272807.jpg": "americas_shingle_logo_with_founding_date.jpg",
    "0038_www_tamko_com_17272807.jpg": "americas_shingle_logo.jpg",
    "0053_www_tamko_com_17272807.jpg": "americas_shingle_logo_with_founding_year.jpg",
    "0083_www_tamko_com_15191510.png": "tamko_75th_anniversary_logo_building_products_since_1944.png",
    "0094_www_tamko_com_48458820.jpg": "heritage_proline_challenge_promotion_extended.jpg",
    "0104_www_malarkeyroofing_com_64033483.jpg": "malarkey_roofing_products_emerald_premium_contractor_emblem.jpg",
    "0128_www_tamko_com_12780518.png": "elite_glass_seal_fiberglass_asphalt_shingles_logo.png",
    "0163_www_malarkeyroofing_com_17160270.jpg": "national_roofing_contractors_association_membership_logo.jpg",
    "BBB Logo.png": "better_business_bureau_bbb_torch_logo.png",
    "classic-heritage-colors-logo.png": "classic_colors_landscape_logo.png",
    "Golden Nail Logo New Transparent.png": "golden_house_and_nail_gn_logo.png",
    "HCI_General.png": "haag_certified_inspector_badge.png",
    "hex-icon---160-wind-warranty-dark.png": "high_wind_speed_emblem_160_mph.png",
    "hex-icon---class-4-dark75fb4098b4c260c68660ff3000f39cfe.png": "class_4_impact_rated_label.png",
    "stormfighter-ir---shingle-construction-illustration.png": "stormfighter_ir_shingle_construction_illustration.png",
    "stormFighter-logo-color.png": "stormfighter_ir_logo_tagline.png",
    "tamko-logo.png": "red_rectangular_outline_on_black_background.png",
    "tamko-storm-fighter-ir.jpg": "stormfighter_ir_ultimate_shingle_protection_easy_installation.jpg",
    "titan-xt-logo-white-red-innovation.png": "titan_xt_logo_innovation_meets_extreme_technology.png"
}

def rename_images():
    """Rename images in the specified folder according to the mappings"""
    
    # Convert to Path object
    folder = Path(folder_path)
    
    # Check if folder exists
    if not folder.exists():
        print(f"Error: Folder not found: {folder_path}")
        return
    
    print(f"Processing folder: {folder_path}")
    print(f"Total mappings: {len(rename_mappings)}")
    print("-" * 50)
    
    success_count = 0
    error_count = 0
    not_found_count = 0
    
    # Process each mapping
    for old_name, new_name in rename_mappings.items():
        old_path = folder / old_name
        new_path = folder / new_name
        
        if old_path.exists():
            try:
                # Check if new name already exists
                if new_path.exists() and old_path != new_path:
                    print(f"⚠️  Warning: {new_name} already exists, skipping {old_name}")
                    error_count += 1
                else:
                    old_path.rename(new_path)
                    print(f"✓ Renamed: {old_name} → {new_name}")
                    success_count += 1
            except Exception as e:
                print(f"✗ Error renaming {old_name}: {e}")
                error_count += 1
        else:
            print(f"- Not found: {old_name}")
            not_found_count += 1
    
    print("-" * 50)
    print(f"Summary:")
    print(f"  Successfully renamed: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Files not found: {not_found_count}")
    print(f"  Total processed: {success_count + error_count + not_found_count}")

if __name__ == "__main__":
    # Ask for confirmation
    print("This script will rename image files in:")
    print(folder_path)
    print()
    response = input("Do you want to continue? (yes/no): ").lower().strip()
    
    if response in ['yes', 'y']:
        rename_images()
        print("\nDone!")
        input("Press Enter to exit...")
    else:
        print("Operation cancelled.")
