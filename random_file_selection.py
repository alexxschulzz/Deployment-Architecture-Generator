import os
import random
import shutil

# Paths to the source and target folders
source_folder = "generatedFiles/full"
target_folder = "generatedFiles/full_random_selection"

# Create the target folder if it does not exist
os.makedirs(target_folder, exist_ok=True)

# List all files in the source folder
files = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]

# Calculate 10% of the files
num_files_to_move = max(1, int(len(files) * 0.1))  # At least 1 file
# num_files_to_move = 50  # Uncomment this line to move a fixed number of files instead

# Randomly select files to move
files_to_move = random.sample(files, num_files_to_move)

# Move the selected files
for file in files_to_move:
    source_path = os.path.join(source_folder, file)
    target_path = os.path.join(target_folder, file)
    shutil.move(source_path, target_path)

# Print the result
print(f"{len(files_to_move)} files have been moved to the folder '{target_folder}'.")