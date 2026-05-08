# Math AA Brain — Claude Code Instructions
## Memory
At the start of every session, read all notes in "Claude Methods/" from Obsidian via mcp-obsidian and apply them to this session.
## Critical Rules
- NEVER write question text into note bodies — always render PNG images from PDFs
- ALWAYS locate Section A in mark scheme PDFs before extracting anything
- Every question note must have exactly 2 outgoing wikilinks: subtopic + paper hub
- Append backlinks to hub notes via GET + PUT — never overwrite existing content
- Handle page.rotation == 90 with: x_display = mediabox_height - y_text
## Pipeline Order
pdf_parser → topic_classifier → vault_populator → image_extractor → ms_image_rebuilder → fix_ms_all → pdf_indexer
