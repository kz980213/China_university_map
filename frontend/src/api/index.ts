// 开发时走 Vite proxy（空字符串 → 同源 /api）；生产时设置 VITE_API_BASE_URL=https://your-render-app.onrender.com
const BASE = (import.meta.env.VITE_API_BASE_URL ?? "") + "/api"

function snakify(obj: Record<string, unknown>): Record<string, unknown> {
  const out: Record<string, unknown> = {}
  for (const [k, v] of Object.entries(obj)) {
    if (v === undefined || v === null || v === "") continue
    out[k.replace(/([A-Z])/g, "_$1").toLowerCase()] = v
  }
  return out
}

// 递归 camelCase 转换，处理嵌套对象和数组（如 SchoolMajorRead.major）
function camelize<T>(obj: unknown): T {
  if (Array.isArray(obj)) return obj.map((item) => camelize(item)) as T
  if (obj !== null && typeof obj === "object") {
    const out: Record<string, unknown> = {}
    for (const [k, v] of Object.entries(obj as Record<string, unknown>)) {
      const ck = k.replace(/_([a-z0-9])/g, (_, c: string) => c.toUpperCase())
      out[ck] = camelize(v)
    }
    return out as T
  }
  return obj as T
}

async function request<T>(url: string, params?: Record<string, unknown>): Promise<T> {
  const qs = params ? "?" + new URLSearchParams(snakify(params) as Record<string, string>) : ""
  const resp = await fetch(BASE + url + qs)
  if (!resp.ok) throw new Error(`${resp.status} ${resp.statusText}`)
  const data = await resp.json()
  return camelize<T>(data)
}

// ── 院校 ──
export async function fetchSchools(params: Record<string, unknown> = {}) {
  return request<{
    items: any[]
    total: number
    page: number
    pageSize: number
    undergraduateCount: number
    juniorCollegeCount: number
    count985: number
    count211: number
    doubleFirstClassCount: number
  }>("/schools", params)
}

export async function fetchSchoolDetail(id: number) {
  return request<any>(`/schools/${id}`)
}

export async function fetchAdmissionScores(id: number, params: Record<string, unknown> = {}) {
  return request<any[]>(`/schools/${id}/admission`, params)
}

// ── 统计 ──
export async function fetchProvinceStats() {
  return request<any[]>("/stats/provinces")
}

// ── 筛选器 ──
export async function fetchFilterProvinces() {
  return request<any[]>("/filters/provinces")
}

export async function fetchFilterSubjects(province: string, year: number) {
  return request<{ province: string; year: number; tracks: string[] }>("/filters/subjects", { province, year })
}

export async function fetchFilterYears() {
  return request<{ minYear: number; maxYear: number }>("/filters/years")
}

// ── 跨院校分数线 ──
export async function fetchAdmissionList(params: Record<string, unknown> = {}) {
  return request<{
    items: any[]
    total: number
    page: number
    pageSize: number
  }>("/admission", params)
}

// ── 志愿推荐 ──
export async function fetchVolunteerRecommend(params: Record<string, unknown>) {
  return request<{
    score: number
    province: string
    year: number
    subjectType: string
    userRank: number | null
    userRankReason: string
    error: string | null
    reach: any[]
    target: any[]
    safety: any[]
  }>("/volunteer/recommend", params)
}

// ── 专业 ──
export async function fetchMajors(params: Record<string, unknown> = {}) {
  return request<{ items: any[]; total: number; page: number; pageSize: number }>("/majors", params)
}

export async function fetchSchoolMajors(schoolId: number) {
  return request<any[]>(`/majors/school/${schoolId}`)
}