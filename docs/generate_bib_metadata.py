#!/usr/bin/env python3
"""
Generate JavaScript metadata from BibTeX file for bibliography filtering.
Run this script whenever you update references.bib
"""

import re
import json
from pathlib import Path


def parse_bibtex_entry(entry_text):
    """Parse a single BibTeX entry and extract metadata."""
    # Extract entry key
    key_match = re.search(r'@\w+\{([^,]+),', entry_text)
    if not key_match:
        return None

    key = key_match.group(1).strip()

    # Extract custom fields
    def get_field(field_name):
        pattern = rf'{field_name}\s*=\s*{{([^}}]+)}}'
        match = re.search(pattern, entry_text)
        return match.group(1).strip() if match else ''

    metadata = {
        'keywords': get_field('keywords'),
        'category': get_field('dynamicalnodes_category'),
        'impl_dynamicalnodes': get_field('impl_dynamicalnodes'),
        'impl_turtlebot': get_field('impl_turtlebot'),
        'impl_crazyflie': get_field('impl_crazyflie'),
    }

    return key, metadata


def generate_metadata_js(bib_file, output_file, var_name='PAPER_METADATA'):
    """Generate JavaScript file with metadata from BibTeX."""
    bib_content = bib_file.read_text()

    # Split into individual entries
    entries = re.split(r'@(?=article|book|inproceedings|proceedings|incollection|misc|phdthesis)', bib_content)

    metadata_dict = {}
    for entry in entries:
        if entry.strip() and not entry.strip().startswith('%'):
            result = parse_bibtex_entry('@' + entry)
            if result:
                key, metadata = result
                metadata_dict[key] = metadata

    # Generate JavaScript content
    js_content = f"""// Auto-generated from {bib_file.name}
// Do not edit manually - run generate_bib_metadata.py instead

const {var_name} = {json.dumps(metadata_dict, indent=2)};
"""

    output_file.write_text(js_content)
    print(f"Generated {output_file} with {len(metadata_dict)} entries")


if __name__ == '__main__':
    script_dir = Path(__file__).parent

    # Generate metadata for main algorithm library
    bib_file = script_dir / 'source' / 'references.bib'
    output_file = script_dir / 'source' / '_static' / 'js' / 'bib_metadata.js'

    if not bib_file.exists():
        print(f"Error: {bib_file} not found")
        exit(1)

    generate_metadata_js(bib_file, output_file, var_name='PAPER_METADATA')

    # Generate metadata for community library
    community_bib_file = script_dir / 'source' / 'community_references.bib'
    community_output_file = script_dir / 'source' / '_static' / 'js' / 'community_bib_metadata.js'

    if community_bib_file.exists():
        generate_metadata_js(community_bib_file, community_output_file, var_name='COMMUNITY_METADATA')
    else:
        print(f"Warning: {community_bib_file} not found (will be created when first contribution is added)")
