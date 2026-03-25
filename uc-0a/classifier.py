import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on the agents.md and skills.md rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "")
    
    # 1. Check for severity keywords for Priority
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    urgent_kw = None
    for kw in severity_keywords:
        if kw in description:
            urgent_kw = kw
            break
            
    priority = "Urgent" if urgent_kw else "Standard"
    
    # 2. Check for Category based on explicitly allowed list
    categories_map = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "waterlog", "inundated"],
        "Streetlight": ["streetlight", "lights out", "light", "dark"],
        "Waste": ["garbage", "waste", "trash", "dead animal", "dump"],
        "Noise": ["music", "noise", "loud"],
        "Road Damage": ["cracked", "broken road", "footpath tiles broken"],
        "Heritage Damage": ["heritage damage", "monument damage"],
        "Heat Hazard": ["heat wave", "sunstroke", "heat"],
        "Drain Blockage": ["drain block", "drain", "sewer", "clog"]
    }
    
    matched_cat = None
    reason_kw = None
    
    for cat, keywords in categories_map.items():
        for kw in keywords:
            if kw in description:
                matched_cat = cat
                reason_kw = kw
                break
        if matched_cat:
            break
            
    # 3. Determine Flag and Reason
    if not matched_cat:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_text = "The description lacks known issue keywords so it requires manual review."
    elif "heritage" in description and "light" in description:
        # Custom ambiguity handler to flag NEEDS_REVIEW
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_text = "The description contains ambiguous references to heritage and lights requiring review."
    else:
        category = matched_cat
        flag = ""
        reason_parts = f"The description mentions '{reason_kw}' classifying it as {category}"
        if urgent_kw:
            reason_parts += f" and mentions '{urgent_kw}' making the priority Urgent"
        reason_text = reason_parts + "."
            
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason_text,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Handles nulls and gracefully skips bad rows.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            
            results = []
            for row in reader:
                try:
                    res = classify_complaint(row)
                    results.append(res)
                except Exception as e:
                    print(f"Skipping malformed row due to error: {e}")
                    
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            print(f"Successfully processed {len(results)} records.")
            
    except FileNotFoundError:
        print(f"Error: The file {input_path} was not found.")
    except Exception as e:
        print(f"Failed to process files: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
