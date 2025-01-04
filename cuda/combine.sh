(find . -type f \( -name "*.cu" -o -name "*.cuh" -o -name "Makefile" \) -print0 | while IFS= read -r -d '' file; do echo -e "\n# $file\n\n\`\`\`cpp"; cat "$file"; echo -e "\n\`\`\`\n"; done) > combined.md

