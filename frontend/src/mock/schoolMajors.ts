import type { SchoolMajor } from '@/types/major'

export const mockSchoolMajors: SchoolMajor[] = [
  // 北京大学 (id: 1)
  { id: 1, schoolId: 1, majorId: 1, collegeName: '信息科学技术学院', tuition: 5000, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: true },
  { id: 2, schoolId: 1, majorId: 9, collegeName: '经济学院', tuition: 5000, duration: '4年', subjectRequirement: '不限', isNationalFirstClass: true, isProvincialFirstClass: true },
  { id: 3, schoolId: 1, majorId: 10, collegeName: '法学院', tuition: 5000, duration: '4年', subjectRequirement: '不限', isNationalFirstClass: true, isProvincialFirstClass: true },
  { id: 4, schoolId: 1, majorId: 13, collegeName: '数学科学学院', tuition: 5000, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: true },
  { id: 5, schoolId: 1, majorId: 11, collegeName: '医学院', tuition: 6000, duration: '5年', subjectRequirement: '化学,生物', isNationalFirstClass: true, isProvincialFirstClass: true },
  { id: 6, schoolId: 1, majorId: 8, collegeName: '物理学院', tuition: 5000, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: true },
  // 清华大学 (id: 2)
  { id: 7, schoolId: 2, majorId: 1, collegeName: '计算机科学与技术系', tuition: 5000, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: true },
  { id: 8, schoolId: 2, majorId: 3, collegeName: '交叉信息研究院', tuition: 5000, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: true },
  { id: 9, schoolId: 2, majorId: 2, collegeName: '软件学院', tuition: 5000, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: true },
  { id: 10, schoolId: 2, majorId: 5, collegeName: '电子工程系', tuition: 5000, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: true },
  { id: 11, schoolId: 2, majorId: 7, collegeName: '自动化系', tuition: 5000, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: true },
  // 南京大学 (id: 9)
  { id: 12, schoolId: 9, majorId: 1, collegeName: '计算机科学与技术系', tuition: 5800, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: true },
  { id: 13, schoolId: 9, majorId: 3, collegeName: '人工智能学院', tuition: 5800, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: false },
  { id: 14, schoolId: 9, majorId: 2, collegeName: '软件学院', tuition: 5800, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: true },
  { id: 15, schoolId: 9, majorId: 8, collegeName: '物理学院', tuition: 5800, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: true },
  { id: 16, schoolId: 9, majorId: 9, collegeName: '商学院', tuition: 5200, duration: '4年', subjectRequirement: '不限', isNationalFirstClass: true, isProvincialFirstClass: true },
  // 东南大学 (id: 10)
  { id: 17, schoolId: 10, majorId: 1, collegeName: '计算机科学与工程学院', tuition: 5800, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: true },
  { id: 18, schoolId: 10, majorId: 2, collegeName: '软件学院', tuition: 5800, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: false },
  { id: 19, schoolId: 10, majorId: 5, collegeName: '信息科学与工程学院', tuition: 5800, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: true },
  { id: 20, schoolId: 10, majorId: 6, collegeName: '信息科学与工程学院', tuition: 5800, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: true },
  { id: 21, schoolId: 10, majorId: 7, collegeName: '自动化学院', tuition: 5800, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: true },
  // 浙江大学 (id: 16)
  { id: 22, schoolId: 16, majorId: 1, collegeName: '计算机科学与技术学院', tuition: 6000, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: true },
  { id: 23, schoolId: 16, majorId: 3, collegeName: '计算机科学与技术学院', tuition: 6000, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: false },
  { id: 24, schoolId: 16, majorId: 2, collegeName: '软件学院', tuition: 6000, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: true },
  { id: 25, schoolId: 16, majorId: 11, collegeName: '医学院', tuition: 6800, duration: '5年', subjectRequirement: '化学,生物', isNationalFirstClass: true, isProvincialFirstClass: true },
  { id: 26, schoolId: 16, majorId: 9, collegeName: '经济学院', tuition: 6000, duration: '4年', subjectRequirement: '不限', isNationalFirstClass: false, isProvincialFirstClass: true },
  // 上海交通大学 (id: 6)
  { id: 27, schoolId: 6, majorId: 5, collegeName: '电子信息与电气工程学院', tuition: 6500, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: true },
  { id: 28, schoolId: 6, majorId: 1, collegeName: '电子信息与电气工程学院', tuition: 6500, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: true },
  { id: 29, schoolId: 6, majorId: 14, collegeName: '机械与动力工程学院', tuition: 5000, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: true },
  { id: 30, schoolId: 6, majorId: 9, collegeName: '安泰经济与管理学院', tuition: 6500, duration: '4年', subjectRequirement: '不限', isNationalFirstClass: true, isProvincialFirstClass: true },
  { id: 31, schoolId: 6, majorId: 11, collegeName: '医学院', tuition: 6500, duration: '5年', subjectRequirement: '化学,生物', isNationalFirstClass: true, isProvincialFirstClass: true },
  // 华中科技大学 (id: 19)
  { id: 32, schoolId: 19, majorId: 1, collegeName: '计算机科学与技术学院', tuition: 5850, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: true },
  { id: 33, schoolId: 19, majorId: 5, collegeName: '电子信息与通信学院', tuition: 5850, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: true },
  { id: 34, schoolId: 19, majorId: 14, collegeName: '机械科学与工程学院', tuition: 4500, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: true },
  { id: 35, schoolId: 19, majorId: 3, collegeName: '人工智能与自动化学院', tuition: 5850, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: false },
  { id: 36, schoolId: 19, majorId: 11, collegeName: '同济医学院', tuition: 5850, duration: '5年', subjectRequirement: '化学,生物', isNationalFirstClass: true, isProvincialFirstClass: true },
  // 电子科技大学 (id: 21)
  { id: 37, schoolId: 21, majorId: 5, collegeName: '电子科学与工程学院', tuition: 4900, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: true },
  { id: 38, schoolId: 21, majorId: 1, collegeName: '计算机科学与工程学院', tuition: 4900, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: true },
  { id: 39, schoolId: 21, majorId: 6, collegeName: '通信与信息工程学院', tuition: 4900, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: true, isProvincialFirstClass: true },
  { id: 40, schoolId: 21, majorId: 2, collegeName: '信息与软件工程学院', tuition: 9800, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: false, isProvincialFirstClass: true },
  { id: 41, schoolId: 21, majorId: 3, collegeName: '计算机科学与工程学院', tuition: 4900, duration: '4年', subjectRequirement: '物理', isNationalFirstClass: false, isProvincialFirstClass: false },
]