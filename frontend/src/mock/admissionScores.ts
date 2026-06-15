import type { AdmissionScore } from '@/types/admission'

let id = 0
function nextId(): number { return ++id }

function generateScores(
  schoolId: number,
  province: string,
  subject: '理科' | '物理类',
  batch: string,
  baseScore: number,
  baseRank: number,
  majorName?: string
): AdmissionScore[] {
  const scores: AdmissionScore[] = []
  // 5年数据，分数和位次有小幅波动
  const yearData: Array<{ year: number; scoreDelta: number; rankDelta: number }> = [
    { year: 2021, scoreDelta: -5, rankDelta: 200 },
    { year: 2022, scoreDelta: -2, rankDelta: 100 },
    { year: 2023, scoreDelta: 0, rankDelta: 0 },
    { year: 2024, scoreDelta: 3, rankDelta: -50 },
    { year: 2025, scoreDelta: 5, rankDelta: -120 },
  ]
  for (const yd of yearData) {
    scores.push({
      id: nextId(),
      schoolId,
      year: yd.year,
      studentProvince: province,
      subjectType: subject,
      batch,
      majorName,
      minScore: baseScore + yd.scoreDelta,
      minRank: baseRank + yd.rankDelta,
      avgScore: baseScore + yd.scoreDelta + 3,
      maxScore: baseScore + yd.scoreDelta + 10,
      enrollmentCount: 30 + Math.round(Math.random() * 10),
      remark: '当前数据为 MVP mock 数据，不可作为真实志愿填报依据。',
      // minRank 是占位假位次（mock 模式下位次列"有数"）。
      // estimatedRank / reason 故意留 undefined——切 API 模式后真实 minRank 大多 NULL、
      // 院校线常是 no_data 显示"暂无"，两种模式位次行为不同构，验收时留意。
      estimatedRank: undefined,
      estimatedRankReason: undefined,
      isSchoolLevel: true,
      matchStatus: 'matched',
    })
  }
  return scores
}

export const mockAdmissionScores: AdmissionScore[] = [
  // ========== 南京大学 在江苏 2021-2025 ==========
  ...generateScores(9, '江苏', '物理类', '本科一批', 660, 800, '计算机科学与技术'),
  ...generateScores(9, '江苏', '物理类', '本科一批', 655, 1200, '人工智能'),
  ...generateScores(9, '江苏', '物理类', '本科一批', 658, 900, '软件工程'),
  ...generateScores(9, '江苏', '物理类', '本科一批', 650, 1500, '物理学'),
  ...generateScores(9, '江苏', '物理类', '本科一批', 647, 1800, '金融学'),

  // ========== 东南大学 在江苏 2021-2025 ==========
  ...generateScores(10, '江苏', '物理类', '本科一批', 630, 4500, '计算机科学与技术'),
  ...generateScores(10, '江苏', '物理类', '本科一批', 625, 5000, '软件工程'),
  ...generateScores(10, '江苏', '物理类', '本科一批', 628, 4700, '电子信息工程'),
  ...generateScores(10, '江苏', '物理类', '本科一批', 622, 5500, '通信工程'),
  ...generateScores(10, '江苏', '物理类', '本科一批', 620, 6000, '自动化'),

  // ========== 浙江大学 在浙江 2021-2025 ==========
  ...generateScores(16, '浙江', '物理类', '本科一批', 655, 700, '计算机科学与技术'),
  ...generateScores(16, '浙江', '物理类', '本科一批', 650, 1100, '人工智能'),
  ...generateScores(16, '浙江', '物理类', '本科一批', 653, 850, '软件工程'),
  ...generateScores(16, '浙江', '物理类', '本科一批', 640, 1800, '临床医学'),
  ...generateScores(16, '浙江', '物理类', '本科一批', 635, 2200, '金融学'),

  // ========== 清华大学 在北京 2021-2025 ==========
  ...generateScores(2, '北京', '物理类', '本科一批', 682, 100, '计算机科学与技术'),
  ...generateScores(2, '北京', '物理类', '本科一批', 680, 150, '人工智能'),
  ...generateScores(2, '北京', '物理类', '本科一批', 678, 200, '软件工程'),
  ...generateScores(2, '北京', '物理类', '本科一批', 675, 250, '电子信息工程'),
  ...generateScores(2, '北京', '物理类', '本科一批', 673, 300, '自动化'),

  // ========== 北京大学 在北京 2021-2025 ==========
  ...generateScores(1, '北京', '物理类', '本科一批', 685, 80, '计算机科学与技术'),
  ...generateScores(1, '北京', '物理类', '本科一批', 683, 120, '数学与应用数学'),
  ...generateScores(1, '北京', '物理类', '本科一批', 680, 160, '物理学'),
  ...generateScores(1, '北京', '物理类', '本科一批', 677, 200, '金融学'),
  ...generateScores(1, '北京', '物理类', '本科一批', 678, 180, '临床医学'),

  // ========== 其他学校和省份 ==========
  ...generateScores(6, '上海', '物理类', '本科一批', 650, 1200, '电子信息工程'),
  ...generateScores(6, '上海', '物理类', '本科一批', 648, 1400, '计算机科学与技术'),
  ...generateScores(19, '湖北', '物理类', '本科一批', 635, 3500, '计算机科学与技术'),
  ...generateScores(19, '湖北', '物理类', '本科一批', 630, 4200, '电子信息工程'),
  ...generateScores(21, '四川', '物理类', '本科一批', 630, 5000, '电子信息工程'),
  ...generateScores(21, '四川', '物理类', '本科一批', 625, 6000, '计算机科学与技术'),
  ...generateScores(21, '四川', '物理类', '本科一批', 620, 7000, '通信工程'),

  // 广东 data
  ...generateScores(13, '广东', '物理类', '本科一批', 645, 2000, '计算机科学与技术'),
  ...generateScores(14, '广东', '物理类', '本科一批', 625, 5000, '计算机科学与技术'),
]