---
name: ugc-flow
description: |
  A UGC-style talking-head review video — a real creator appears on camera and speaks while reviewing or showcasing a specific product.
---
# ugc-flow

UGC-style talking-head pipeline. Creative prompt-writing delegated to backend enhancers.

## Pipeline
1. Parse request + product analysis
2. Character generation (Soul 2.0) or user-provided photo
3. Upload product
4. Draft full monologue
5. Generate boards sequentially
6. Write Seedance prompts in parallel
7. Submit Seedance jobs in parallel
8. Poll, download, stitch
9. Report + optional post package

## Duration → N boards
| Total D | N boards |
| 4-15 | 1 | 16-19 | 2 | 20-30 | 2 | 31-45 | 3 | 46-60 | 4 | >60 | ceil(D/15) |