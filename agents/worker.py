#!/usr/bin/env python3
"""簡易ワーカー：mission_board.md を読み、CSV/TSV の基本統計量を計算して agents/output.txt に結果を書き出す

機能:
- pandas があればそれを使って数値列の基本統計量を出力する
- pandas が無ければダミー出力を作る
"""
import argparse
from pathlib import Path
import datetime
import sys


def read_mission(mission_path: Path) -> str:
    if not mission_path.exists():
        return "(no mission_board.md found)"
    return mission_path.read_text(encoding="utf-8")


def compute_with_pandas(data_path: Path):
    import pandas as pd

    # 自動で区切り文字を推定する簡易ローダー
    if data_path.suffix.lower() in (".csv", ".tsv"):
        sep = "," if data_path.suffix.lower() == ".csv" else "\t"
        df = pd.read_csv(data_path, sep=sep)
    else:
        # 試しにCSVとして読む
        df = pd.read_csv(data_path)

    numeric = df.select_dtypes("number")
    stats = numeric.describe().transpose()
    return stats.to_csv()


def run_sample_task(output_path: Path, data_path: Path = None) -> None:
    now = datetime.datetime.utcnow().isoformat() + "Z"
    out_lines = [f"run_time: {now}", f"data_path: {data_path or '(none)'}"]

    if data_path and data_path.exists():
        try:
            csv_stats = compute_with_pandas(data_path)
            out_lines.append("-- stats (CSV-format) --")
            out_lines.append(csv_stats)
        except Exception as e:
            out_lines.append(f"ERROR computing stats with pandas: {e}")
    else:
        out_lines.append("- step: load_dummy_data")
        out_lines.append("- step: compute_simple_stat: mean=42")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(out_lines), encoding="utf-8")
    print("WROTE:", output_path)


def write_json_output(output_path: Path, data_path: Path = None, stats=None, notes=None, errors=None):
    import json

    now = datetime.datetime.utcnow().isoformat() + "Z"
    payload = {
        "run_time": now,
        "task_id": None,
        "data_path": str(data_path) if data_path else None,
        "summary": None,
        "stats": stats,
        "notes": notes,
        "errors": str(errors) if errors else None,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("WROTE JSON:", output_path)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sample", action="store_true", help="run sample task")
    p.add_argument("--run", action="store_true", help="run with optional --data")
    p.add_argument("--data", help="path to CSV/TSV data file")
    p.add_argument("--mission", default="agents/mission_board.md", help="mission board path")
    p.add_argument("--out", default=None, help="output path (default agents/output.txt or agents/output.json depending on --format)")
    p.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    args = p.parse_args()

    mission_text = read_mission(Path(args.mission))
    print("MISSION:\n", mission_text)

    data_path = Path(args.data) if args.data else None

    # determine default output path based on format
    if args.out:
        out = Path(args.out)
    else:
        out = Path("agents/output.json") if args.format == "json" else Path("agents/output.txt")

    if args.sample:
        if args.format == "json":
            # produce dummy json
            write_json_output(out, data_path, stats=None, notes="sample run", errors=None)
        else:
            run_sample_task(out, data_path)
    elif args.run:
        # try to run real computation; prefer pandas if available
        try:
            import pandas  # type: ignore
            try:
                # compute stats
                if data_path and data_path.exists():
                    csv_stats = compute_with_pandas(data_path)
                    if args.format == "json":
                        # minimal JSON stats wrapper
                        write_json_output(out, data_path, stats={"csv_stats": csv_stats}, notes="processed with pandas", errors=None)
                    else:
                        run_sample_task(out, data_path)
                else:
                    if args.format == "json":
                        write_json_output(out, None, stats=None, notes="no data provided", errors=None)
                    else:
                        run_sample_task(out, None)
            except Exception as e:
                if args.format == "json":
                    write_json_output(out, data_path, stats=None, notes=None, errors=e)
                else:
                    print(f"ERROR during computation: {e}", file=sys.stderr)
        except Exception:
            print("pandas が見つかりません。--sample でダミー実行します。", file=sys.stderr)
            if args.format == "json":
                write_json_output(out, None, stats=None, notes="pandas not installed - sample run", errors=None)
            else:
                run_sample_task(out, None)
    else:
        print("何も実行しません。--sample か --run を付けてください。")


if __name__ == "__main__":
    main()
