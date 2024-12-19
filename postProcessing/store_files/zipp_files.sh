#!/bin/bash

# Base folder containing the files
base_folder="..../DLFiles"
output_folder="..../zippedPDF"


for hex1 in {0..f}; do
    for hex2 in {0..f}; do
        # Combination pattern
        pattern="${hex1}${hex2}*"

        # ZIP file name
        zip_file="$output_folder/${hex1}${hex2}.zip"

        # Find matching files and zip them
        matching_files=$(find "$base_folder" -type f -name "$pattern")
        if [ -n "$matching_files" ]; then
            zip -r "$zip_file" "$base_folder" -i "$base_folder/$pattern"
            echo "Created $zip_file for pattern $pattern"
        else
            echo "No files found for pattern $pattern"
        fi
    done
done