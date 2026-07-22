"""L1 格式校验阶段校验器包（v16 T2 §3）。

使用方式：
    from ai_workflow.validators import L1S1Validator, L1S2Validator, ...

    validator = L1S5Validator()
    result = validator.run_l1_check(Path("test_points.json"), context={"s4_ids": {...}})
"""

from .l1_s1 import L1S1Validator
from .l1_s2 import L1S2Validator
from .l1_s3 import L1S3Validator
from .l1_s4 import L1S4Validator
from .l1_s5 import L1S5Validator
from .l1_s6 import L1S6Validator
from .l1_s7 import L1S7Validator

__all__ = [
    "L1S1Validator",
    "L1S2Validator",
    "L1S3Validator",
    "L1S4Validator",
    "L1S5Validator",
    "L1S6Validator",
    "L1S7Validator",
]

# 便捷工厂函数
_STAGE_VALIDATORS: dict[str, type] = {
    "S1": L1S1Validator,
    "S2": L1S2Validator,
    "S3": L1S3Validator,
    "S4": L1S4Validator,
    "S5": L1S5Validator,
    "S6": L1S6Validator,
    "S7": L1S7Validator,
}


def get_validator(stage: str) -> type:
    """根据阶段名获取对应的 L1 校验器类。"""
    if stage not in _STAGE_VALIDATORS:
        raise ValueError(f"未知阶段 '{stage}'，支持的阶段：{sorted(_STAGE_VALIDATORS.keys())}")
    return _STAGE_VALIDATORS[stage]
