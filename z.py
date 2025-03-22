import json
import os
from pathlib import Path

def add_colors_to_patterns(json_data):
    # Define the color lists for each group
    group1_colors = ["D55E00", "56B4E9", "CC79A7"]
    group2_colors = ["0072B2", "009E73", "F0E442", "725DEF", "DD217D", "E69F00"]
    
    # Find the two group keys from the json data
    group_keys = list(json_data.keys())
    if len(group_keys) != 2:
        return None  # Not a valid template file
    
    try:
        # Add colors to first group
        for i, pattern in enumerate(json_data[group_keys[0]]):
            pattern["colour"] = group1_colors[i]
        
        # Add colors to second group
        for i, pattern in enumerate(json_data[group_keys[1]]):
            pattern["colour"] = group2_colors[i]
        
        return json_data
    except (KeyError, TypeError, IndexError):
        return None  # Return None if the file doesn't have the expected structure

def process_template_files():
    # Get the current directory
    current_dir = Path.cwd()
    
    # Find all JSON files with 'left' or 'right' in the name
    json_files = list(current_dir.glob('*left*.json')) + list(current_dir.glob('*right*.json'))
    
    for file_path in json_files:
        try:
            # Read the JSON file
            with open(file_path, 'r') as f:
                json_data = json.load(f)
            
            # Process the file
            updated_data = add_colors_to_patterns(json_data)
            
            # If the file was successfully processed, save it back
            if updated_data is not None:
                with open(file_path, 'w') as f:
                    json.dump(updated_data, f, indent=4)
                print(f"Successfully processed: {file_path}")
            else:
                print(f"Skipped non-template file: {file_path}")
                
        except json.JSONDecodeError:
            print(f"Skipped invalid JSON file: {file_path}")
            continue
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            continue

if __name__ == "__main__":
    process_template_files()

'''
import os
import json

def add_colors_to_patterns(directory_path):
    # Define the color lists for each group
    first_group_colors = ["D55E00", "56B4E9", "CC79A7"]
    second_group_colors = ["0072B2", "009E73", "F0E442", "725DEF", "DD217D", "E69F00"]
    
    # Find all JSON files with 'left' or 'right' in the name
    json_files = [f for f in os.listdir(directory_path) 
                 if ('left' in f.lower() or 'right' in f.lower()) and f.endswith('.json')]
    
    for filename in json_files:
        file_path = os.path.join(directory_path, filename)
        
        try:
            # Load the JSON file
            with open(file_path, 'r') as file:
                try:
                    json_data = json.load(file)
                    
                    # Check if this is a template file (should have exactly two group keys)
                    if not isinstance(json_data, dict):
                        print(f"Skipping {filename}: not a JSON object")
                        continue
                    
                    # Get the group names (first two keys in the JSON)
                    group_names = list(json_data.keys())
                    if len(group_names) < 2:
                        print(f"Skipping {filename}: doesn't have at least two groups")
                        continue
                    
                    # Add colors to the first group
                    first_group = group_names[0]
                    for i, pattern in enumerate(json_data[first_group]):
                        if i < len(first_group_colors):
                            pattern["colour"] = first_group_colors[i]
                    
                    # Add colors to the second group
                    second_group = group_names[1]
                    for i, pattern in enumerate(json_data[second_group]):
                        if i < len(second_group_colors):
                            pattern["colour"] = second_group_colors[i]
                    
                    # Write the updated data back to the file with same indentation
                    with open(file_path, 'w') as outfile:
                        json.dump(json_data, outfile, indent=4)
                        
                    print(f"Updated colors in {filename}")
                    
                except json.JSONDecodeError:
                    print(f"Skipping {filename}: not a valid JSON file")
                    continue
                
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            continue

add_colors_to_patterns('./')
'''