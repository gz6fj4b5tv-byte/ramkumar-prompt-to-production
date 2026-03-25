# skills.md

skills:
  - name: classify_complaint
    description: Classifies one complaint row by determining its category, priority, reason, and flag based on the text description.
    input: A string description of a single citizen complaint.
    output: A record containing category (exact string match), priority (Urgent/Standard/Low), reason (one sentence string), and flag (NEEDS_REVIEW or blank).
    error_handling: If input is genuinely ambiguous or unclassifiable, output category must be 'Other' and flag must be 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: File paths for the input CSV (--input) and the output CSV (--output).
    output: A newly created CSV file at the specified output path with classified rows.
    error_handling: If input file is missing or unreadable, halt execution and raise a file not found/read error. If individual rows are malformed, skip them or flag them for review.
