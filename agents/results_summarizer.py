from pathlib import Path
import re
import json

METRICS = Path('research/artifacts/metrics.json')
FINAL = Path('research/artifacts/final_draft.md')
FINAL_JA = Path('research/artifacts/final_draft_japanese.md')


def main():
    if not METRICS.exists():
        print('No metrics.json found; run experiments first')
        return
    metrics = json.loads(METRICS.read_text(encoding='utf-8'))
    text = FINAL.read_text(encoding='utf-8') if FINAL.exists() else '# Draft Paper\n\n'
    results_block = f"## Results\n\n- workspace smoke-test accuracy: {metrics.get('accuracy')}\n\n"
    if '## Results' in text:
        text = re.sub(r"## Results\n(?:.*?\n)*?(?=\n## |\Z)", results_block, text, flags=re.S)
    else:
        text = text + '\n' + results_block
    FINAL.write_text(text, encoding='utf-8')
    if FINAL_JA.exists():
        text_ja = FINAL_JA.read_text(encoding='utf-8')
        results_block_ja = f"## 結果\n\n- ワークスペースのスモークテスト精度: {metrics.get('accuracy')}\n\n"
        if '## 結果' in text_ja:
            text_ja = re.sub(r"## 結果\n(?:.*?\n)*?(?=\n## |\Z)", results_block_ja, text_ja, flags=re.S)
        else:
            text_ja = text_ja + '\n' + results_block_ja
        FINAL_JA.write_text(text_ja, encoding='utf-8')
    print('results_summarizer: final_draft.md updated')


if __name__ == '__main__':
    main()
