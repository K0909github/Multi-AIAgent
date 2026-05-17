from pathlib import Path
import json

IN_MD = Path('research/artifacts/hypotheses.md')
OUT_JSON = Path('research/artifacts/selected_hypothesis.json')
OUT_MD = Path('research/artifacts/selected_hypothesis.md')


def extract_hypotheses(text):
    lines = [l.strip() for l in text.splitlines()]
    hyps = [l[2:].strip() for l in lines if l.startswith('- ')]
    return hyps


def score_hypothesis(h):
    # cheap heuristic: shorter hypotheses prioritized; deterministic score
    return -len(h)


def main():
    if not IN_MD.exists():
        print('No hypotheses.md found; run research_workflow first')
        return
    text = IN_MD.read_text(encoding='utf-8')
    hyps = extract_hypotheses(text)
    if not hyps:
        print('No hypotheses found')
        return
    scored = sorted([(h, score_hypothesis(h)) for h in hyps], key=lambda x: x[1], reverse=True)
    selected = scored[0][0]
    OUT_JSON.write_text(json.dumps({'selected': selected}, ensure_ascii=False, indent=2), encoding='utf-8')
    OUT_MD.write_text('# Selected Hypothesis\n\n- ' + selected + '\n', encoding='utf-8')
    print('hypothesis_selector: selected hypothesis written')


if __name__ == '__main__':
    main()
