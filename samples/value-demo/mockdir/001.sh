#!/bin/sh
echo "RATIONALE: T1 — add() is the highest-priority ready task"
cat >> calc.py <<'EOF'

def add(a, b):
    return a + b
EOF
cat >> tests/test_calc.py <<'EOF'


def test_add():
    import calc

    assert calc.add(2, 3) == 5
EOF
pytest -q
python3 -c "
import pathlib
p = pathlib.Path('.kelix/backlog.md')
p.write_text(p.read_text().replace('- [ ] T1:', '- [x] T1:'))
"
git add -A && git commit -q -m "T1: add function"
