#!/bin/sh
echo "RATIONALE: T2 — sub() is the highest-priority ready task"
cat >> calc.py <<'EOF'

def sub(a, b):
    return a - b
EOF
cat >> tests/test_calc.py <<'EOF'


def test_sub():
    import calc

    assert calc.sub(5, 3) == 2
EOF
pytest -q
python3 -c "
import pathlib
p = pathlib.Path('.kelix/backlog.md')
p.write_text(p.read_text().replace('- [ ] T2:', '- [x] T2:'))
"
git add -A && git commit -q -m "T2: sub function"
