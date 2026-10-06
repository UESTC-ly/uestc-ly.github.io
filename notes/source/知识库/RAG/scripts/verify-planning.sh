#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"

command -v rg >/dev/null || {
  echo "ERROR: authoring check requires rg" >&2
  exit 1
}

for file in \
  SPECIFICATION.md PROJECT_PLAN.md ACCEPTANCE_MATRIX.md CONTENT_MANIFEST.md \
  STYLE_GUIDE.md GLOSSARY.md CODE_CONVENTIONS.md DIAGRAM_CONVENTIONS.md \
  DEPENDENCY_MATRIX.md QUALITY_CHECKLIST.md PROGRESS.md SOURCE_REGISTER.md \
  DATA_LICENSES.md THIRD_PARTY_NOTICES.md reports/README.md; do
  test -s "$file" || {
    echo "ERROR: missing required file: $file" >&2
    exit 1
  }
done

missing_manifest=0
while IFS= read -r file; do
  if ! rg -Fq "$file" CONTENT_MANIFEST.md; then
    echo "ERROR: Manifest does not register $file" >&2
    missing_manifest=1
  fi
done < <(rg --files -g '!**/.git/**' -g '!**/.omx/**' -g '!**/AGENTS.md' | sort)
test "$missing_manifest" -eq 0

duplicate_ids=$(
  sed -n 's/^| \([A-Z][A-Z0-9-]*\) |.*/\1/p' ACCEPTANCE_MATRIX.md |
    rg -v '^ID$' | sort | uniq -d
)
test -z "$duplicate_ids" || {
  printf 'ERROR: duplicate requirement IDs:\n%s\n' "$duplicate_ids" >&2
  exit 1
}

test "$(rg -c '^\| AC[0-9]{2} \|' ACCEPTANCE_MATRIX.md)" -eq 22
test "$(rg -c '^\| BASIC-[0-9]{2} \|' ACCEPTANCE_MATRIX.md)" -eq 7
test "$(rg -c '^\| CAP-[0-9]{2} \|' ACCEPTANCE_MATRIX.md)" -eq 2
test "$(rg -c '^\| D[0-9]{2} \|' ACCEPTANCE_MATRIX.md)" -eq 20

for role in \
  'Curriculum Architect' 'Foundations' 'RAG Theory' 'Data Pipeline' \
  'Retrieval Engineering' 'Generation and Prompting' 'Implementation' \
  'Evaluation' 'Advanced RAG' 'Production Engineering' \
  'Security and Governance' 'Technical Reviewer' 'Code Verification' \
  'Beginner Experience' 'Managing Editor'; do
  rg -Fq "| $role |" PROJECT_PLAN.md || {
    echo "ERROR: missing Agent role: $role" >&2
    exit 1
  }
done

while IFS= read -r file; do
  h1_count=$(rg -c '^# ' "$file")
  test "$h1_count" -eq 1 || {
    echo "ERROR: $file has $h1_count level-one headings" >&2
    exit 1
  }
done < <(rg --files -g '*.md' -g '!**/.omx/**' -g '!**/AGENTS.md')

if rg -n '[ \t]+$' -g '*.md' -g '!**/.omx/**'; then
  echo "ERROR: trailing whitespace found" >&2
  exit 1
fi

test "$(wc -l < SPECIFICATION.md | tr -d ' ')" -eq 1618
git diff --check

delivery_count=$(rg --files -g '!**/.git/**' -g '!**/.omx/**' -g '!**/AGENTS.md' | wc -l | tr -d ' ')
markdown_count=$(rg --files -g '*.md' -g '!**/.omx/**' -g '!**/AGENTS.md' | wc -l | tr -d ' ')
id_count=$(
  sed -n 's/^| \([A-Z][A-Z0-9-]*\) |.*/\1/p' ACCEPTANCE_MATRIX.md |
    rg -v '^ID$' | wc -l | tr -d ' '
)

printf 'PASS delivery=%s markdown=%s ids=%s AC=22 BASIC=7 CAP=2 D=20 roles=15 specification_lines=1618\n' \
  "$delivery_count" "$markdown_count" "$id_count"
