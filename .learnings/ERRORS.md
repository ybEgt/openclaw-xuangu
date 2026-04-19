## [ERR-20260419-001] mx-xuangu-integration

**Logged**: 2026-04-19T20:24:00+08:00
**Priority**: high
**Status**: in_progress
**Area**: config

### Summary
把演示/模拟进化逻辑混入真实妙想选股链路，导致前序自检与实证验证边界不清。

### Error
```
mx_xuangu_integrated.py / mx_xuangu_integrated_fixed.py 包含大量模拟胜率、演示输出、测试模式回退，容易制造“已优化”的假象。
```

### Context
- 用户连续要求深度自检、自我进化、反推进化
- 早期工作更多是流程自检而非真实历史样本反推
- 真实选股链路应以 skills/mx-xuangu/mx_xuangu.py 与真实历史CSV为准

### Suggested Fix
- 把演示脚本与真实验证脚本彻底分离
- 真实审计只读取历史CSV/JSON，不使用模拟胜率
- 后续反推进化以实证表为准，不再引用演示输出

### Metadata
- Reproducible: yes
- Related Files: mx_xuangu_integrated.py, mx_xuangu_integrated_fixed.py, mx_strategy_audit.py
- See Also: none

---
