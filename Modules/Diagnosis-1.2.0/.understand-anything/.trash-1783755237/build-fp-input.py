import json
from pathlib import Path

with open(r'E:\diagnosis\.understand-anything\intermediate\scan-result.json') as f:
    scan = json.load(f)

# The fingerprint script needs sourceFilePaths
# Use the files from scan-result.json (29 files)
source_paths = [f['path'] for f in scan['files']]

fp_input = {
    'projectRoot': r'E:\diagnosis',
    'sourceFilePaths': source_paths,
    'gitCommitHash': '2ad29b87e9f0c13940f7c3809ee28929547bf49f'
}

out = r'E:\diagnosis\.understand-anything\intermediate\fingerprint-input.json'
with open(out, 'w', encoding='utf-8') as f:
    json.dump(fp_input, f, indent=2)
print(f'Written fingerprint-input.json with {len(source_paths)} files')
print(f'Source paths: {source_paths[:5]}...')