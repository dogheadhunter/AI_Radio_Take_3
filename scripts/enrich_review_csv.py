"""Enrich review CSV with script text and audio paths for human reviewability."""
from pathlib import Path
import csv
import json
import argparse


def find_audit_json(script_id: str, audit_dir: Path):
    """Find audit JSON for a script ID in passed/failed folders."""
    for subdir in ['passed', 'failed']:
        json_path = audit_dir / subdir / f"{script_id}.json"
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    return None


def load_generated_for_audit_dir(audit_dir: Path):
    """Load generated_scripts.json from audit directory."""
    gen_json = audit_dir / "generated_scripts.json"
    if gen_json.exists():
        with open(gen_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {s['script_id']: s for s in data.get('scripts', [])}
    return {}


def find_in_samples(script_id: str, manual_validation_dir: Path):
    """Find script in samples_passed.json or samples_failed.json."""
    for sample_file in ['samples_passed.json', 'samples_failed.json']:
        sample_path = manual_validation_dir / sample_file
        if sample_path.exists():
            with open(sample_path, 'r', encoding='utf-8') as f:
                samples = json.load(f)
                for sample in samples:
                    if sample.get('script_id') == script_id:
                        return sample
    return None


def find_script_text_file(script_id: str, data_dir: Path):
    """Search data/generated for script text files."""
    for txt_file in data_dir.glob("**/*.txt"):
        if script_id in txt_file.stem:
            with open(txt_file, 'r', encoding='utf-8') as f:
                return f.read()
    return None


def enrich_review_csv(review_csv: Path, output_csv: Path, audit_dir: Path):
    """Add script_text and audio_path columns to review CSV."""
    manual_validation_dir = review_csv.parent
    data_dir = Path("data")
    
    # Load generated scripts index
    generated_index = load_generated_for_audit_dir(audit_dir)
    
    # Read existing review CSV
    with open(review_csv, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Enrich each row
    for row in rows:
        script_id = row['script_id']
        
        # Try multiple fallback strategies
        script_text = ""
        audio_path = ""
        
        # 1. Check audit JSON
        audit_data = find_audit_json(script_id, audit_dir)
        if audit_data:
            script_text = audit_data.get('script_content', '')
            audio_path = audit_data.get('audio_path', '')
        
        # 2. Check generated_scripts.json
        if not script_text and script_id in generated_index:
            script_text = generated_index[script_id].get('text', '')
            audio_path = generated_index[script_id].get('audio_path', '')
        
        # 3. Check samples JSONs
        if not script_text:
            sample_data = find_in_samples(script_id, manual_validation_dir)
            if sample_data:
                script_text = sample_data.get('script_content', '')
                audio_path = sample_data.get('audio_path', '')
        
        # 4. Search filesystem
        if not script_text:
            script_text = find_script_text_file(script_id, data_dir) or ""
        
        row['script_text'] = script_text
        row['audio_path'] = audio_path
    
    # Write enriched CSV
    if rows:
        fieldnames = list(rows[0].keys())
        with open(output_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"Wrote enriched CSV to {output_csv}")
    else:
        print("No rows to enrich")


def main():
    parser = argparse.ArgumentParser(description="Enrich review CSV with script text")
    parser.add_argument("--review", required=True, help="Path to review.csv")
    parser.add_argument("--out", required=True, help="Output path for enriched CSV")
    parser.add_argument("--audit-dir", help="Audit directory (auto-detected if omitted)")
    args = parser.parse_args()
    
    review_csv = Path(args.review)
    output_csv = Path(args.out)
    
    # Auto-detect latest audit dir if not provided
    if args.audit_dir:
        audit_dir = Path(args.audit_dir)
    else:
        audit_dirs = sorted(Path("data/audit").glob("*"), reverse=True)
        audit_dir = audit_dirs[0] if audit_dirs else Path("data/audit")
    
    enrich_review_csv(review_csv, output_csv, audit_dir)


if __name__ == "__main__":
    main()
