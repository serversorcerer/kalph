#!/bin/sh
echo "RATIONALE: T5 — cli entrypoint is the highest-priority ready task"
cat >> calc.py <<'EOF'

def main(argv):
    op, a, b = argv[0], float(argv[1]), float(argv[2])
    ops = {"add": add, "sub": sub, "mul": mul, "div": div}
    return ops[op](a, b)
EOF
cat >> tests/test_calc.py <<'EOF'


def test_main():
    import calc

    assert calc.main(["add", "1", "2"]) == 3
EOF
pytest -q
python3 -c "
import pathlib
p = pathlib.Path('.kelix/backlog.md')
p.write_text(p.read_text().replace('- [ ] T5:', '- [x] T5:'))
"
git add -A && git commit -q -m "T5: cli entrypoint"
echo "KELIX COMPLETE"
