"""Small test harness for the TypeScript parser stub.

Creates a temporary TypeScript file and runs the parser, printing a summary.
"""
from __future__ import annotations

import os
import sys
import shutil

# Ensure repository root is on sys.path so `indexer` package can be imported
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
  sys.path.insert(0, REPO_ROOT)

from indexer.typescript_parser import parse_repository_typescript
from indexer.resolver.semantic_resolver import TypeScriptSemanticResolver


def write_sample(root: str):
    os.makedirs(root, exist_ok=True)
    sample = '''
import { foo } from './lib'
import bar from "./bar"

export function login(user) {
  verifyToken(user.token)
  return getUser(user.id)
}

class Service {
  start() {
    this.run()
  }
  run() {
    console.log('run')
  }
}

function helper() {
  console.log('helper')
}
'''
    # Add richer constructs
    sample += '''

/**
 * Auth interface
 */
export interface Auth {
  userId: string;
  token: string;
}

enum Status { Ok, Error }

type ID = string | number

@decorator()
export class Controller extends Service implements Runnable {
  constructor(private repo) { super(); }
  handle(req: Request): Response {
    return helper();
  }
}
'''
    p = os.path.join(root, "sample.ts")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(sample)
    return p


def main():
    tmp = "scripts/tmp_ts"
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    write_sample(tmp)
    repo = parse_repository_typescript(tmp)
    print(f"Files: {len(repo.files)}")
    for path, f in repo.files.items():
      print(f"- {path}: symbols={len(f.symbols)}, imports={len(f.imports)}, functions={len(f.functions)}")
      for s in f.symbols:
        print(f"  * SYMBOL: id={s.id} name={s.name} kind={s.kind} loc={s.location}")

    # Run a semantic resolver example
    resolver = TypeScriptSemanticResolver(repo)
    # Example: resolve call 'helper' across repository
    matches = resolver.resolve_call('helper')
    print(f"Resolved 'helper' -> {len(matches)} matches")
    for m in matches:
        print(f"  - {m.id} ({m.kind}) @ {m.location}")


if __name__ == '__main__':
    main()
