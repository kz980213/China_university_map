/**
 * 全国各省高校统计常量（数据来源：Supabase schools 表聚合查询）。
 * province 字段使用短名称，与 ECharts 地图组件和筛选器保持一致。
 * 如需更新，在 Supabase SQL Editor 执行：
 *
 * SELECT province,
 *   COUNT(*) AS total,
 *   SUM(CASE WHEN level = '本科' THEN 1 ELSE 0 END) AS undergraduate_count,
 *   SUM(CASE WHEN level <> '本科' THEN 1 ELSE 0 END) AS junior_college_count,
 *   SUM(CASE WHEN is_985 THEN 1 ELSE 0 END) AS count985,
 *   SUM(CASE WHEN is_211 THEN 1 ELSE 0 END) AS count211,
 *   SUM(CASE WHEN is_double_first_class THEN 1 ELSE 0 END) AS double_first_class_count
 * FROM schools GROUP BY province ORDER BY total DESC;
 */

import type { ProvinceStat } from '@/types/school'

export const PROVINCE_STATS: ProvinceStat[] = [
  { province: '河南',  total: 178, undergraduateCount: 62,  juniorCollegeCount: 116, count985: 0, count211: 1,  doubleFirstClassCount: 2  },
  { province: '江苏',  total: 175, undergraduateCount: 82,  juniorCollegeCount: 93,  count985: 2, count211: 11, doubleFirstClassCount: 16 },
  { province: '山东',  total: 167, undergraduateCount: 72,  juniorCollegeCount: 95,  count985: 2, count211: 3,  doubleFirstClassCount: 3  },
  { province: '广东',  total: 166, undergraduateCount: 77,  juniorCollegeCount: 89,  count985: 2, count211: 4,  doubleFirstClassCount: 8  },
  { province: '湖南',  total: 147, undergraduateCount: 54,  juniorCollegeCount: 93,  count985: 2, count211: 3,  doubleFirstClassCount: 4  },
  { province: '四川',  total: 141, undergraduateCount: 55,  juniorCollegeCount: 86,  count985: 2, count211: 5,  doubleFirstClassCount: 8  },
  { province: '湖北',  total: 134, undergraduateCount: 70,  juniorCollegeCount: 64,  count985: 2, count211: 7,  doubleFirstClassCount: 7  },
  { province: '河北',  total: 131, undergraduateCount: 63,  juniorCollegeCount: 68,  count985: 0, count211: 1,  doubleFirstClassCount: 1  },
  { province: '安徽',  total: 126, undergraduateCount: 50,  juniorCollegeCount: 76,  count985: 1, count211: 3,  doubleFirstClassCount: 3  },
  { province: '江西',  total: 117, undergraduateCount: 49,  juniorCollegeCount: 68,  count985: 0, count211: 1,  doubleFirstClassCount: 1  },
  { province: '辽宁',  total: 114, undergraduateCount: 64,  juniorCollegeCount: 50,  count985: 2, count211: 4,  doubleFirstClassCount: 4  },
  { province: '浙江',  total: 111, undergraduateCount: 65,  juniorCollegeCount: 46,  count985: 1, count211: 1,  doubleFirstClassCount: 3  },
  { province: '陕西',  total: 98,  undergraduateCount: 61,  juniorCollegeCount: 37,  count985: 3, count211: 7,  doubleFirstClassCount: 7  },
  { province: '北京',  total: 92,  undergraduateCount: 69,  juniorCollegeCount: 23,  count985: 8, count211: 26, doubleFirstClassCount: 34 },
  { province: '云南',  total: 92,  undergraduateCount: 35,  juniorCollegeCount: 57,  count985: 0, count211: 1,  doubleFirstClassCount: 1  },
  { province: '福建',  total: 90,  undergraduateCount: 41,  juniorCollegeCount: 49,  count985: 1, count211: 2,  doubleFirstClassCount: 2  },
  { province: '广西',  total: 89,  undergraduateCount: 41,  juniorCollegeCount: 48,  count985: 0, count211: 1,  doubleFirstClassCount: 1  },
  { province: '山西',  total: 82,  undergraduateCount: 36,  juniorCollegeCount: 46,  count985: 0, count211: 1,  doubleFirstClassCount: 2  },
  { province: '贵州',  total: 80,  undergraduateCount: 32,  juniorCollegeCount: 48,  count985: 0, count211: 1,  doubleFirstClassCount: 1  },
  { province: '黑龙江',total: 80,  undergraduateCount: 40,  juniorCollegeCount: 40,  count985: 1, count211: 4,  doubleFirstClassCount: 4  },
  { province: '重庆',  total: 75,  undergraduateCount: 29,  juniorCollegeCount: 46,  count985: 1, count211: 2,  doubleFirstClassCount: 2  },
  { province: '上海',  total: 69,  undergraduateCount: 40,  juniorCollegeCount: 29,  count985: 4, count211: 9,  doubleFirstClassCount: 14 },
  { province: '吉林',  total: 68,  undergraduateCount: 40,  juniorCollegeCount: 28,  count985: 1, count211: 3,  doubleFirstClassCount: 3  },
  { province: '新疆',  total: 67,  undergraduateCount: 26,  juniorCollegeCount: 41,  count985: 0, count211: 2,  doubleFirstClassCount: 2  },
  { province: '天津',  total: 56,  undergraduateCount: 31,  juniorCollegeCount: 25,  count985: 2, count211: 3,  doubleFirstClassCount: 5  },
  { province: '内蒙古',total: 54,  undergraduateCount: 21,  juniorCollegeCount: 33,  count985: 0, count211: 1,  doubleFirstClassCount: 1  },
  { province: '甘肃',  total: 49,  undergraduateCount: 28,  juniorCollegeCount: 21,  count985: 1, count211: 1,  doubleFirstClassCount: 1  },
  { province: '海南',  total: 28,  undergraduateCount: 11,  juniorCollegeCount: 17,  count985: 0, count211: 1,  doubleFirstClassCount: 1  },
  { province: '宁夏',  total: 22,  undergraduateCount: 10,  juniorCollegeCount: 12,  count985: 0, count211: 1,  doubleFirstClassCount: 1  },
  { province: '青海',  total: 13,  undergraduateCount: 6,   juniorCollegeCount: 7,   count985: 0, count211: 1,  doubleFirstClassCount: 1  },
  { province: '西藏',  total: 8,   undergraduateCount: 5,   juniorCollegeCount: 3,   count985: 0, count211: 1,  doubleFirstClassCount: 1  },
]
