export const API_BASE_URL = 'http://localhost:8000'

export interface SizeStock {
  size: string
  quantity: number
}

export interface ProductSummary {
  product_id: string
  name: string
  garment_type: string
  short_description: string
  price: number
  image_url: string
}

export interface ProductDetail {
  product_id: string
  name: string
  garment_type: string
  description: string
  colors: string[]
  price: number
  image_url: string
  sizes: SizeStock[]
  total_stock: number
}

export function mediaUrl(path: string): string {
  return `${API_BASE_URL}${path}`
}

export async function fetchProducts(): Promise<ProductSummary[]> {
  const res = await fetch(`${API_BASE_URL}/products`)
  if (!res.ok) {
    throw new Error(`Failed to load products (${res.status})`)
  }
  return res.json()
}

export async function fetchProduct(productId: string): Promise<ProductDetail> {
  const res = await fetch(`${API_BASE_URL}/products/${productId}`)
  if (!res.ok) {
    throw new Error(`Failed to load product (${res.status})`)
  }
  return res.json()
}

export interface AuthUser {
  id: number
  first_name: string | null
  last_name: string | null
  email: string
  created_at: string
}

export interface RegisterPayload {
  first_name: string
  last_name: string
  email: string
  password: string
}

export interface LoginPayload {
  email: string
  password: string
}

async function parseAuthError(res: Response): Promise<string> {
  try {
    const body = await res.json()
    if (typeof body.detail === 'string') return body.detail
  } catch {
    // fall through to generic message
  }
  return 'Something went wrong. Please try again.'
}

export async function registerUser(payload: RegisterPayload): Promise<AuthUser> {
  const res = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    throw new Error(await parseAuthError(res))
  }
  return res.json()
}

export async function loginUser(payload: LoginPayload): Promise<AuthUser> {
  const res = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    throw new Error(await parseAuthError(res))
  }
  return res.json()
}

export interface ChatReply {
  reply: string
  mentioned_product_ids: string[]
}

export interface ChatHistoryEntry {
  role: 'user' | 'assistant'
  content: string
  product_ids: string[]
  created_at: string
}

export interface SendChatOptions {
  userId?: number
  currentProductId?: string
}

export async function sendChatMessage(
  message: string,
  options: SendChatOptions = {},
): Promise<ChatReply> {
  const res = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      user_id: options.userId ?? null,
      current_product_id: options.currentProductId ?? null,
    }),
  })
  if (!res.ok) {
    throw new Error(await parseAuthError(res))
  }
  return res.json()
}

export async function fetchChatHistory(userId: number): Promise<ChatHistoryEntry[]> {
  const res = await fetch(`${API_BASE_URL}/chat/history/${userId}`)
  if (!res.ok) {
    throw new Error(`Failed to load chat history (${res.status})`)
  }
  return res.json()
}
