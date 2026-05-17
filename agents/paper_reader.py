from pathlib import Path
import json

ARTIFACT = Path('research/artifacts/summary.md')
OUT_MD = Path('research/artifacts/summary.reviewed.md')
OUT_JSON = Path('research/artifacts/summary_review.json')


def main():
    if not ARTIFACT.exists():
        print('No summary.md found; run research_workflow first')
        return
    text = ARTIFACT.read_text(encoding='utf-8')
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    key = [l[2:].strip() for l in lines if l.startswith('- ') and not l.lower().startswith('- source:')]
    reviewed = text + '\n\n' + '## Auto-reviewed notes\n' + '\n'.join(f'- {l}' for l in key[:4])
    OUT_MD.write_text(reviewed, encoding='utf-8')
    OUT_JSON.write_text(json.dumps({'key_points': key[:4]}, ensure_ascii=False, indent=2), encoding='utf-8')
    print('paper_reader: wrote', OUT_MD, OUT_JSON)


if __name__ == '__main__':
    main()
