import os
import sys
import subprocess
import shutil
from pathlib import Path
import argparse


def run(cmd, cwd=None):
    print('>',' '.join(cmd))
    res = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(res.stdout)
    if res.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return res.stdout


def clone_repo(repo_url, dest, branch=None):
    dest_path = Path(dest)
    if dest_path.exists():
        print(f"Destination {dest} already exists, skipping clone")
        return dest_path
    run(['git', 'clone', repo_url, dest])
    if branch:
        run(['git', 'checkout', branch], cwd=str(dest_path))
    return dest_path


def find_candidate_files(repo_dir):
    p = Path(repo_dir)
    candidates = []
    for pattern in ('**/net*.py', '**/*net*.py', '**/train*.py', '**/train_*.py', '**/train_model.py'):
        for f in p.glob(pattern):
            if f.is_file():
                candidates.append(f)
    return list(dict.fromkeys(candidates))


def backup_file(path: Path):
    bak = path.with_suffix(path.suffix + '.magent.bak')
    shutil.copy2(path, bak)
    print(f'Backed up {path} -> {bak}')


def append_adapter(target_file: Path, generated_code_relpath: str):
    backup_file(target_file)
    adapter = f"\n# === BEGIN Multi-AIAgent AUTO-INTEGRATION ===\n" \
              + "import os, sys\n" \
              + "_mg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))\n" \
              + f"_scaffold = os.path.abspath(os.path.join(_mg_root, '{generated_code_relpath}'))\n" \
              + "if _scaffold not in sys.path:\n    sys.path.insert(0, _scaffold)\n" \
              + "# Try to import scaffold train if present\n" \
              + "try:\n    from train import train as _magent_scaffold_train\n    def run_magent_scaffold(*args, **kwargs):\n        return _magent_scaffold_train(*args, **kwargs)\nexcept Exception as e:\n    # scaffold not available or import failed\n    _magent_scaffold_train = None\n    def run_magent_scaffold(*args, **kwargs):\n        raise RuntimeError('Multi-AIAgent scaffold not available: ' + str(e))\n" \
              + "# === END Multi-AIAgent AUTO-INTEGRATION ===\n"
    with target_file.open('a', encoding='utf-8') as fh:
        fh.write(adapter)
    print(f'Appended adapter to {target_file}')


def integrate(repo_url, dest, generated_code, branch=None, create_branch=None):
    repo_dir = clone_repo(repo_url, dest, branch=branch)
    candidates = find_candidate_files(repo_dir)
    print('Found candidate files:', candidates)
    # compute relative path from repo_dir to generated_code
    gen_path = Path(generated_code).resolve()
    try:
        rel = os.path.relpath(str(gen_path), start=str(repo_dir.resolve()))
    except Exception:
        rel = str(gen_path)

    if not candidates:
        print('No candidate files found to patch. Exiting.')
        return

    if create_branch:
        run(['git', 'checkout', '-b', create_branch], cwd=str(repo_dir))

    for f in candidates:
        try:
            append_adapter(f, rel)
        except Exception as e:
            print(f'Failed to append adapter to {f}: {e}')

    # commit
    run(['git', 'add', '.'], cwd=str(repo_dir))
    run(['git', 'commit', '-m', 'chore: integrate Multi-AIAgent scaffold adapter'], cwd=str(repo_dir))
    print('Integration complete. Review changes and push as needed.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', required=True, help='Git URL of the target repo (e.g. https://github.com/yi-ding-cs/LGG)')
    parser.add_argument('--dest', default='external/LGG', help='Destination path to clone into')
    parser.add_argument('--generated', default='research/generated_code', help='Path to generated scaffold (relative to this repo)')
    parser.add_argument('--branch', help='Branch to checkout after clone')
    parser.add_argument('--create-branch', help='Create a branch to commit integration changes')
    args = parser.parse_args()

    integrate(args.repo, args.dest, args.generated, branch=args.branch, create_branch=args.create_branch)


if __name__ == '__main__':
    main()
