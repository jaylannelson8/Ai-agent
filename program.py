import json
import os

input_dir = "./inputfiles/"
output_dir = "./outputfiles/"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

cleaned_students = []
skipped_records = []
failed_files = []
processed_files_count = 0
total_records_found = 0
seen_ids = set()

filenames = ["file1.json", "file2.json", "file3.json", "file4.json", "file5.json"]

for filename in filenames:
    path = os.path.join(input_dir, filename)
    try:
        with open(path, "r") as f:
            data = json.load(f)
        
        processed_files_count += 1
        
        internal_list = []
        if isinstance(data, list):
            internal_list = data
        elif isinstance(data, dict):
            if "students" in data and isinstance(data["students"], list):
                internal_list = data["students"]
            else:
                internal_list = [data]
        
        for record in internal_list:
            total_records_found += 1
            
            s_id = record.get("id")
            s_name = record.get("name")

            # Decision: Discard records with missing IDs to ensure the uniqueness requirement is met.
            if s_id is None or s_name is None:
                skipped_records.append({"data": record, "reason": "Missing required fields (id or name)"})
                continue

            try:
                clean_id = int(float(s_id))
                
                if clean_id in seen_ids:
                    skipped_records.append({"data": record, "reason": f"Duplicate ID: {clean_id}"})
                    continue

                major = str(record.get("major")) if record.get("major") else "Undeclared"
                
                gpa = record.get("gpa")
                try:
                    if gpa is not None:
                        gpa = float(gpa)
                        if not (0.0 <= gpa <= 4.0):
                            gpa = None
                except:
                    gpa = None

                credits = record.get("credits")
                try:
                    clean_credits = int(float(credits)) if credits is not None else 0
                except:
                    clean_credits = 0

                valid_student = {
                    "id": clean_id,
                    "name": str(s_name),
                    "major": major,
                    "gpa": gpa,
                    "credits": clean_credits
                }
                cleaned_students.append(valid_student)
                seen_ids.add(clean_id)

            except:
                skipped_records.append({"data": record, "reason": "Invalid data format or types"})

    except Exception as e:
        failed_files.append({"file": filename, "reason": str(e)})

with open(os.path.join(output_dir, "cleaned_students.json"), "w") as f:
    json.dump(cleaned_students, f, indent=4)

valid_gpas = [s["gpa"] for s in cleaned_students if s["gpa"] is not None]
avg_gpa = sum(valid_gpas) / len(valid_gpas) if valid_gpas else 0

summary_data = {
    "total_files_processed": processed_files_count,
    "total_records_found": total_records_found,
    "total_valid_records": len(cleaned_students),
    "total_skipped_records": len(skipped_records),
    "average_gpa": round(avg_gpa, 2)
}
with open(os.path.join(output_dir, "summary.json"), "w") as f:
    json.dump(summary_data, f, indent=4)

with open(os.path.join(output_dir, "errors.log"), "w") as f:
    f.write("FILES FAILED TO LOAD:\n")
    for fail in failed_files:
        f.write(f"- {fail['file']}: {fail['reason']}\n")
    f.write("\nRECORDS SKIPPED:\n")
    for skip in skipped_records:
        f.write(f"- Reason: {skip['reason']} | Data: {skip['data']}\n")