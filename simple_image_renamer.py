import os
from pathlib import Path

# Define the folder path
folder_path = r"S:\DriveSyncFiles\WORK MAIN\GOLDEN WEBSITE\SHINGLES"

# Define the rename mappings
rename_mappings = {
    "0001_www_tamko_com_24200632.jpg": "TAMKO_Dark-Grey-Charcoal_Shingles.jpg",
    "0002_www_tamko_com_64254235.jpg": "TAMKO_Charcoal-Black_Shingles.jpg",
    "0003_www_tamko_com_38773436.jpg": "TAMKO_Brown-Grey_Mottled_Shingles.jpg",
    "0008_www_homedepot_com_10166520.jpg": "Dark-Grey_Black_Shingles.jpg",
    "0008_www_tamko_com_17644330.jpg": "TAMKO_Reddish-Brown_to_Black_Shingles.jpg",
    "0009_www_tamko_com_13137619.jpg": "TAMKO_Dark-Charcoal_with_Rust_Shingles.jpg",
    "0012_www_tamko_com_90105302.jpg": "TAMKO_Warm_Earthy-Brown_Shingles.jpg",
    "0014_www_homedepot_com_26509872.jpg": "Brown_to_Rust_Variegated_Shingles.jpg",
    "0014_www_tamko_com_29042910.jpg": "TAMKO_Brown-Grey_Layered_Shingles.jpg",
    "0015_www_homedepot_com_35129868.jpg": "Dark-Grey_Coarse_Shingles.jpg",
    "0016_www_tamko_com_84270174.jpg": "TAMKO_Tan_Golden-Brown_Mix_Shingles.jpg",
    "0018_www_homedepot_com_53875977.jpg": "Charcoal-Grey_with_Beige_Speckle_Shingles.jpg",
    "0019_www_tamko_com_21310859.jpg": "TAMKO_Golden-Tan_to_Dark-Brown_Shingles.jpg",
    "0028_www_homedepot_com_10166520.jpg": "Deep-Black_Shingles.jpg",
    "0033_www_homedepot_com_35129868.jpg": "Graphite-Grey_Granular_Shingles.jpg",
    "0036_www_homedepot_com_53875977.jpg": "Grey-Brown_Mottled_Shingles.jpg",
    "0039_www_homedepot_com_37390044.jpg": "Dark-Brown_with_Golden_Highlights_Shingles.jpg",
    "0048_www_malarkeyroofing_com_47283580.jpg": "Photorhey_Brown_Shingle_Backdrop.jpg",
    "0049_www_homedepot_com_42590757.jpg": "Uniform_Charcoal_Black_Shingles.jpg",
    "0056_www_tamko_com_24200632.jpg": "TAMKO_Dark-Grey_Black_Speckled_Shingles.jpg",
    "0057_www_homedepot_com_99612193.jpg": "Charcoal_Grey_Shingles.jpg",
    "0057_www_tamko_com_38773436.jpg": "TAMKO_Brown_to_Charcoal_Variegated_Shingles.jpg",
    "0064_www_tamko_com_21310859.jpg": "TAMKO_Light-to-Dark_Brown_Shingles.jpg",
    "0067_www_tamko_com_75362098.jpg": "TAMKO_Reddish-Brown_Earthy_Shingles.jpg",
    "0069_www_tamko_com_58703948.jpg": "TAMKO_Dark-Grey_Weathered_Shingles.jpg",
    "0070_www_tamko_com_86100242.jpg": "TAMKO_Solid_Black_Shingles.jpg",
    "0073_www_tamko_com_12915015.jpg": "TAMKO_Grey-Black_Speckled_Shingles.jpg",
    "0074_www_tamko_com_36499432.jpg": "TAMKO_Jagged_Edge_Slate-Grey_Shingles.jpg",
    "0075_www_tamko_com_62529038.jpg": "TAMKO_Silvery-to_Dark_Grey_Shingles.jpg",
    "0089_www_tamko_com_66658176.jpg": "TAMKO_3-Tone_Grey_Brown_Tan_Shingles.jpg",
    "0099_www_homedepot_com_53505786.jpg": "Brown_and_Dark-Grey_Ridge_Shingles.jpg",
    "0105_www_tamko_com_64254235.jpg": "TAMKO_Dark-Grey_Black_Shingles.jpg",
    "0106_www_tamko_com_17644330.jpg": "TAMKO_Terracotta_Brown_Speckled_Shingles.jpg",
    "0109_www_tamko_com_90105302.jpg": "TAMKO_Brown-Red_Rustic_Shingles.jpg",
    "0110_www_tamko_com_29042910.jpg": "TAMKO_Brown_Grey_Multi-Tone_Shingles.jpg",
    "0113_www_homedepot_com_43173765.jpg": "Brown_with_Tan_and_Grey_Ridge_Shingles.jpg",
    "0113_www_tamko_com_78666125.jpg": "TAMKO_Brown_with_Blue-Grey_Accents_Shingles.jpg",
    "0115_www_tamko_com_28732571.jpg": "TAMKO_Silver-to_Charcoal_Grey_Shingles.jpg",
    "0117_www_tamko_com_70823536.jpg": "TAMKO_Golden-Brown_to_Dark_Shingles.jpg",
    "0118_www_tamko_com_16067957.jpg": "TAMKO_Grey_Black_Brown_Speckled_Shingles.jpg",
    "0119_www_tamko_com_17367387.jpg": "TAMKO_Light-to_Charcoal_Grey_Shingles.jpg",
    "0120_www_tamko_com_66931819.jpg": "TAMKO_Multi-Tone_Brown_Grey_Orange_Shingles.jpg",
    "0122_www_tamko_com_45122149.jpg": "TAMKO_Beige_to_Brown_Mottled_Shingles.jpg",
    "0123_www_tamko_com_34757080.jpg": "TAMKO_Grey_with_Light-Brown_Shingles.jpg",
    "0124_www_tamko_com_80167541.jpg": "TAMKO_Dark_Green_Shingles.jpg",
    "0154_www_tamko_com_64254235.jpg": "TAMKO_Matte_Charcoal_Black_Shingles.jpg",
    "0155_www_tamko_com_17644330.jpg": "TAMKO_Brown_to_Charcoal_Rustic_Shingles.jpg",
    "0158_www_tamko_com_90105302.jpg": "TAMKO_Rich_Brown_Reddish_Shingles.jpg",
    "0159_www_tamko_com_29042910.jpg": "TAMKO_Brown_Grey_Earthy_Shingles.jpg",
    "0163_www_tamko_com_78666125.jpg": "TAMKO_Multi-Earth_Tone_Shingles.jpg",
    "0165_www_tamko_com_28732571.jpg": "TAMKO_Dimensional_Grey_Black_Shingles.jpg",
    "0167_www_tamko_com_70823536.jpg": "TAMKO_Dark-to_Golden_Brown_Shingles.jpg",
    "0168_www_tamko_com_16067957.jpg": "TAMKO_Grey_Black_Tan_Speckled_Shingles.jpg",
    "0169_www_tamko_com_17367387.jpg": "TAMKO_Light-Medium-Dark_Grey_Shingles.jpg",
    "0170_www_tamko_com_66931819.jpg": "TAMKO_Brown_Burnt-Orange_Grey_Shingles.jpg",
    "0172_www_tamko_com_45122149.jpg": "TAMKO_Brown_Tan_Light-Grey_Shingles.jpg",
    "0173_www_tamko_com_34757080.jpg": "TAMKO_Weathered_Grey_Shingles.jpg",
    "jalen1wa_IMAGINE_a_slow_zoom-in_transition_that_brings_the_ca_a22ba30e-48f3-42e8-b4ca-35f7482b334a_2.png": "Wet_Dark_Shingle_Close-up.png",
    "jalen1wa_IMAGINE_the_camera_shifting_to_a_POV_shot_from_the_r_3433de9a-3e6f-46ff-acd5-484f82257b17_3.png": "Roof_and_Gutter_Wet_Dark_Grey.png",
    "Metal_Roof.jpg": "Metal_Roof_(no_text)_Image.jpg"
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
