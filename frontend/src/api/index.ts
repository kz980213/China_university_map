// 开发时走 Vite proxy（空字符串 → 同源 /api）；生产时设置 VITE_API_BASE_URL=https://your-render-app.onrender.com
const BASE = (import.meta.env.VITE_API_BASE_URL ?? "") + "/api"

// ─────────────────────────────────────────────────────────────────────────────
// 模块级缓存（页面生命周期内有效，跨组件/跨路由共享）
// 只缓存静态/半静态数据：筛选器选项、省份统计
// 分页/用户查询不缓存，避免占用内存
// ─────────────────────────────────────────────────────────────────────────────
const _cache = new Map<string, unknown>()
const _inflight = new Map<string, Promise<unknown>>()

const CACHE_PREFIXES = ["/filters/", "/stats/provinces"]

function isCacheable(url: string): boolean {
  return CACHE_PREFIXES.some((p) => url.startsWith(p))
}

// ─────────────────────────────────────────────────────────────────────────────
// 工具函数
// ─────────────────────────────────────────────────────────────────────────────
function snakify(obj: Record<string, unknown>): Record<string, unknown> {
  const out: Record<string, unknown> = {}
  for (const [k, v] of Object.entries(obj)) {
    if (v === undefined || v === null || v === "") continue
    out[k.replace(/([A-Z])/g, "_$1").toLowerCase()] = v
  }
  return out
}

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

// ─────────────────────────────────────────────────────────────────────────────
// 带重试的 fetch（处理 Render 免费套餐冷启动 502/503）
// 策略：最多重试 3 次，等待 3s → 6s → 9s，覆盖约 20s 的冷启动窗口
// ─────────────────────────────────────────────────────────────────────────────
async function fetchJSON(fullUrl: string): Promise<unknown> {
  const MAX_RETRIES = 3
  const BASE_DELAY = 3000

  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    const resp = await fetch(fullUrl)
    if (resp.ok) return resp.json()

    const retryable = resp.status === 502 || resp.status === 503 || resp.status === 504
    if (retryable && attempt < MAX_RETRIES) {
      await new Promise((r) => setTimeout(r, BASE_DELAY * (attempt + 1)))
      continue
    }
    throw new Error(`${resp.status} ${resp.statusText}`)
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// 核心请求函数
// ─────────────────────────────────────────────────────────────────────────────
async function request<T>(url: string, params?: Record<string, unknown>): Promise<T> {
  const qs = params
    ? "?" + new URLSearchParams(snakify(params) as Record<string, string>)
    : ""
  const fullUrl = BASE + url + qs
  const cacheable = isCacheable(url)

  // 命中缓存直接返回
  if (cacheable && _cache.has(fullUrl)) {
    return _cache.get(fullUrl) as T
  }

  // 并发同一请求时共享同一个 Promise，避免重复发出
  if (cacheable && _inflight.has(fullUrl)) {
    return _inflight.get(fullUrl) as Promise<T>
  }

  const promise = fetchJSON(fullUrl)
    .then((data) => {
      const result = camelize<T>(data)
      if (cacheable) _cache.set(fullUrl, result)
      _inflight.delete(fullUrl)
      return result
    })
    .catch((err) => {
      _inflight.delete(fullUrl)
      throw err
    })

  if (cacheable) _inflight.set(fullUrl, promise)
  return promise
}

// ─────────────────────────────────────────────────────────────────────────────
// API 函数
// ─────────────────────────────────────────────────────────────────────────────

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

// ── 筛选器（均命中缓存） ──
export async function fetchFilterProvinces() {
  return request<any[]>("/filters/provinces")
}

export async function fetchFilterSubjects(province: string, year: number) {
  return request<{ province: string; year: number; tracks: string[] }>(
    "/filters/subjects",
    { province, year },
  )
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
