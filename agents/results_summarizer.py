from pathlib import Path
import json

METRICS = Path('research/artifacts/metrics.json')
FINAL = Path('research/artifacts/final_draft.md')


def main():
    if not METRICS.exists():
        print('No metrics.json found; run experiments first')
        return
    metrics = json.loads(METRICS.read_text(encoding='utf-8'))
    text = FINAL.read_text(encoding='utf-8') if FINAL.exists() else '# Draft Paper\n\n'
    # Simple replacement: insert results under Results section
    results_block = f"## Results\n\nAuto-inserted results:\n\n- accuracy: {metrics.get('accuracy')}\n\n"
    if '## Results' in text:
        text = text.replace('## Results\nTODO: insert results tables and statistical tests.', results_block)
    else:
        text = text + '\n' + results_block
    FINAL.write_text(text, encoding='utf-8')
    print('results_summarizer: final_draft.md updated')


if __name__ == '__main__':
    main()
