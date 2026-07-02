#!/bin/sh
echo "RATIONALE: T4 — div() with zero guard is the highest-priority ready task"
cat >> calc.py <<'EOF'

def div(a, b):
    if b == 0:
        raise ValueError("division by zero")
    return a / b
EOF
cat >> tests/test_calc.py <<'EOF'


def test_div():
    import calc

    assert calc.div(8, 2) == 4
EOF
pytest -q
python3 -c "
import pathlib
p = pathlib.Path('.kelix/backlog.md')
p.write_text(p.read_text().replace('- [ ] T4:', '- [x] T4:'))
"
git add -A && git commit -q -m "T4: div with zero guard"
