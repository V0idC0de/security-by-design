#!/usr/bin/env bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <file-path>"
    exit 1
fi

file="$1"

commit_messages1=(
    "Add README.md"
    "Add basic functionality"
    "Fix bug in input validation"
    "Improve error handling"
    "Refactor code structure"
    "Update documentation"
    "Optimize performance"
    "Add unit tests"
)
commit_messages2=(
    "Fix typo in comments"
    "Update dependencies"
    "Improve logging"
    "Add configuration options"
    "Remove deprecated code"
    "Enhance security checks"
    "Update README"
)

for msg in "${commit_messages1[@]}"; do
    echo "" >> "$file"
    git add "$file"
    git commit -m "$msg"
done

# Add Secret to commit history
cp "$file" "$file.bak"
jq '.db_repo_pat = "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"' "$file" > tmpfile
mv tmpfile "$file"
git add "$file"
git commit -m "Debug DB connection"
# Remove again
mv "$file.bak" "$file"
git add "$file"
git commit -m "Remove debug settings"

for msg in "${commit_messages2[@]}"; do
    echo "" >> "$file"
    git add "$file"
    git commit -m "$msg"
done

jq '.' "$file" > tmpfile
mv tmpfile "$file"
git add "$file"
git commit -m "Format files"
