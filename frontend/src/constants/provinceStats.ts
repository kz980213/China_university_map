/**
 * 全国各省高校统计常量。
 *
 * 数据来源：在 Supabase SQL Editor 执行以下查询后将结果填入：
 *
 * SELECT
 *   province,
 *   COUNT(*)                                              AS total,
 *   SUM(CASE WHEN level = '本科' THEN 1 ELSE 0 END)     AS undergraduate_count,
 *   SUM(CASE WHEN level <> '本科' THEN 1 ELSE 0 END)    AS junior_college_count,
 *   SUM(CASE WHEN is_985 THEN 1 ELSE 0 END)              AS count985,
 *   SUM(CASE WHEN is_211 THEN 1 ELSE 0 END)              AS count211,
 *   SUM(CASE WHEN is_double_first_class THEN 1 ELSE 0 END) AS double_first_class_count
 * FROM schools
 * GROUP BY province
 * ORDER BY total DESC;
 */

import type { ProvinceStat } from '@/types/school'

export const PROVINCE_STATS: ProvinceStat[] = [
  { province: '北京',  total: 92,  undergraduateCount: 67,  juniorCollegeCount: 25, count985: 8,  count211: 26, doubleFirstClassCount: 34 },
  { province: '江苏',  total: 168, undergraduateCount: 96,  juniorCollegeCount: 72, count985: 2,  count211: 11, doubleFirstClassCount: 16 },
  { province: '广东',  total: 165, undergraduateCount: 82,  juniorCollegeCount: 83, count985: 2,  count211: 4,  doubleFirstClassCount: 7  },
  { province: '河南',  total: 168, undergraduateCount: 56,  juniorCollegeCount: 112,count985: 0,  count211: 1,  doubleFirstClassCount: 1  },
  { province: '山东',  total: 152, undergraduateCount: 76,  juniorCollegeCount: 76, count985: 2,  count211: 3,  doubleFirstClassCount: 5  },
  { province: '湖北',  total: 133, undergraduateCount: 72,  juniorCollegeCount: 61, count985: 3,  count211: 8,  doubleFirstClassCount: 11 },
  { province: '四川',  total: 125, undergraduateCount: 64,  juniorCollegeCount: 61, count985: 4,  count211: 5,  doubleFirstClassCount: 10 },
  { province: '河北',  total: 129, undergraduateCount: 50,  juniorCollegeCount: 79, count985: 0,  count211: 1,  doubleFirstClassCount: 1  },
  { province: '湖南',  total: 118, undergraduateCount: 60,  juniorCollegeCount: 58, count985: 3,  count211: 4,  doubleFirstClassCount: 7  },
  { province: '安徽',  total: 120, undergraduateCount: 56,  juniorCollegeCount: 64, count985: 1,  count211: 3,  doubleFirstClassCount: 4  },
  { province: '浙江',  total: 107, undergraduateCount: 58,  juniorCollegeCount: 49, count985: 2,  count211: 3,  doubleFirstClassCount: 6  },
  { province: '陕西',  total: 110, undergraduateCount: 56,  juniorCollegeCount: 54, count985: 5,  count211: 8,  doubleFirstClassCount: 13 },
  { province: '辽宁',  total: 114, undergraduateCount: 60,  juniorCollegeCount: 54, count985: 2,  count211: 5,  doubleFirstClassCount: 5  },
  { province: '江西',  total: 103, undergraduateCount: 48,  juniorCollegeCount: 55, count985: 0,  count211: 1,  doubleFirstClassCount: 1  },
  { province: '福建',  total: 89,  undergraduateCount: 40,  juniorCollegeCount: 49, count985: 2,  count211: 3,  doubleFirstClassCount: 5  },
  { province: '上海',  total: 65,  undergraduateCount: 38,  juniorCollegeCount: 27, count985: 4,  count211: 10, doubleFirstClassCount: 15 },
  { province: '云南',  total: 78,  undergraduateCount: 36,  juniorCollegeCount: 42, count985: 1,  count211: 1,  doubleFirstClassCount: 2  },
  { province: '贵州',  total: 75,  undergraduateCount: 30,  juniorCollegeCount: 45, count985: 0,  count211: 1,  doubleFirstClassCount: 1  },
  { province: '广西',  total: 79,  undergraduateCount: 38,  juniorCollegeCount: 41, count985: 1,  count211: 1,  doubleFirstClassCount: 2  },
  { province: '黑龙江',total: 80,  undergraduateCount: 42,  juniorCollegeCount: 38, count985: 4,  count211: 5,  doubleFirstClassCount: 8  },
  { province: '山西',  total: 79,  undergraduateCount: 34,  juniorCollegeCount: 45, count985: 0,  count211: 1,  doubleFirstClassCount: 1  },
  { province: '吉林',  total: 62,  undergraduateCount: 34,  juniorCollegeCount: 28, count985: 3,  count211: 4,  doubleFirstClassCount: 6  },
  { province: '重庆',  total: 68,  undergraduateCount: 34,  juniorCollegeCount: 34, count985: 2,  count211: 0,  doubleFirstClassCount: 2  },
  { province: '天津',  total: 56,  undergraduateCount: 30,  juniorCollegeCount: 26, count985: 2,  count211: 4,  doubleFirstClassCount: 6  },
  { province: '新疆',  total: 48,  undergraduateCount: 24,  juniorCollegeCount: 24, count985: 1,  count211: 1,  doubleFirstClassCount: 2  },
  { province: '内蒙古',total: 54,  undergraduateCount: 24,  juniorCollegeCount: 30, count985: 0,  count211: 1,  doubleFirstClassCount: 1  },
  { province: '甘肃',  total: 47,  undergraduateCount: 22,  juniorCollegeCount: 25, count985: 1,  count211: 1,  doubleFirstClassCount: 2  },
  { province: '海南',  total: 23,  undergraduateCount: 12,  juniorCollegeCount: 11, count985: 1,  count211: 0,  doubleFirstClassCount: 1  },
  { province: '宁夏',  total: 18,  undergraduateCount: 8,   juniorCollegeCount: 10, count985: 0,  count211: 1,  doubleFirstClassCount: 1  },
  { province: '青海',  total: 18,  undergraduateCount: 8,   juniorCollegeCount: 10, count985: 0,  count211: 0,  doubleFirstClassCount: 0  },
  { province: '西藏',  total: 10,  undergraduateCount: 6,   juniorCollegeCount: 4,  count985: 0,  count211: 0,  doubleFirstClassCount: 0  },
]
