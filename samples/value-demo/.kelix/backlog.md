# Value demo backlog

- [ ] T1: add() function | priority: 90 | status: ready | by: owner | phase: P-CALC | req: REQ-C1
  rationale: addition is the first calculator operation
  details: add(a,b) in calc.py; assert calc.add(2,3)==5 in tests/test_calc.py

- [ ] T2: sub() function | priority: 80 | status: ready | by: owner | deps: T1 | phase: P-CALC | req: REQ-C2
  rationale: subtraction completes basic binary ops pair
  details: sub(a,b) in calc.py; assert calc.sub(5,3)==2 in tests/test_calc.py

- [ ] T3: mul() function | priority: 70 | status: ready | by: owner | deps: T2 | phase: P-CALC | req: REQ-C3
  rationale: multiplication extends the API surface
  details: mul(a,b) in calc.py; assert calc.mul(4,3)==12 in tests/test_calc.py

- [ ] T4: div() with zero guard | priority: 60 | status: ready | by: owner | deps: T3 | phase: P-CALC | req: REQ-C4
  rationale: division must fail safely on zero divisor
  details: div(a,b) raises ValueError on b==0; assert calc.div(8,2)==4 in tests/test_calc.py

- [ ] T5: cli entrypoint | priority: 50 | status: ready | by: owner | deps: T4 | phase: P-CALC | req: REQ-C5
  rationale: a main() entrypoint proves the module is usable from argv
  details: main(argv) dispatches add/sub/mul/div; assert calc.main(['add','1','2'])==3 in tests/test_calc.py
