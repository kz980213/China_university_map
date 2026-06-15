"""专业分数线导入存根——占位说明，此脚本不执行实际导入。

专业线数据来源（待确认后实施）：
  - 每条记录包含院校、专业、招生省份、年份、科目类型、最低分/最低位次等字段
  - 对应 admission_scores 表中 is_school_level=False 的行
  - major_id 需与 majors 表关联；raw_major_name/raw_major_code 保留原始字段

入库时的 CHECK 约束合规要求：
  - is_school_level=False（专业线）
  - major_id / major_name / raw_major_name / raw_major_code / score_subject_req
    均可正常填写（ck_school_level_no_major_fields 只限制 is_school_level=True 时）

import_batch 格式建议：
  "{source}_{YYYYMMDD}"，如 "gaokao_major_20260611"

TODO：待数据来源确定后，按此框架实现正式导入脚本。
"""
