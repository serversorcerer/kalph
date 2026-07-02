#!/bin/sh
echo "RATIONALE: T3 — mul() is the highest-priority ready task"
cat >> calc.py <<'EOF'

def mul(a, b):
    return a * b
EOF
cat >> tests/test_calc.py <<'EOF'


def test_mul():
    import calc

    assert calc.mul(4, 3) == 12
EOF
pytest -q
python3 -c "
import pathlib
p = pathlib.Path('.kelix/backlog.md')
p.write_text(p.read_text().replace('- [ ] T3:', '- [x] T3:'))
"
git add -A && git commit -q -m "T3: mul function"
