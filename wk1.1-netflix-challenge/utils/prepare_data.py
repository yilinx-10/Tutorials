import os
import pandas as pd

import kagglehub


if __name__ == "__main__":
    # Download latest version
    path = kagglehub.dataset_download("netflix-inc/netflix-prize-data")
    print("Path to dataset files:", path)
    
    # Create output directory if it doesn't exist
    os.makedirs('cleaned-dataset-csv', exist_ok=True)

    # Get file names
    original_files = [f for f in os.listdir(path) if "combined_data" in f]

    # Loop over the original files and clean them up
    for filename in original_files:
        new_lines = []
        print(f"Working on file {filename}...")

        # Open the file filename, identify the movieID and add it to corresponding rows
        with open(f"{path}/{filename}") as data:
            for line in data:
                if ":\n" in line:
                    movieID = line.strip(":\n")
                else:
                    new_line = movieID+","+line
                    new_line = new_line.strip("\n").split(",")
                    new_lines.append(new_line)

            # Save to new file
            df = pd.DataFrame(new_lines)
            new_filename = "cleaned_" + filename.replace("txt", "csv")
            df.to_csv(f'cleaned-dataset-csv/{new_filename}', header=False, index=False)

            print("Done!")
            print(f"Stored to {new_filename}")
