import { useEffect, useRef, useState, type FormEvent } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { fetchChatHistory, fetchProduct, mediaUrl, sendChatMessage, type ProductDetail } from '../api'
import { useAuth } from '../context/AuthContext'
import './ChatWidget.css'

interface ChatMessage {
  role: 'user' | 'assistant'
  text: string
  productIds?: string[]
}

const GREETING: ChatMessage = {
  role: 'assistant',
  text: "Hi! I'm the Campus Customs shop assistant. Ask me about any of our gear.",
}

function truncate(text: string, limit = 90): string {
  const trimmed = text.trim()
  return trimmed.length <= limit ? trimmed : `${trimmed.slice(0, limit - 1).trimEnd()}…`
}

function getCurrentProductId(pathname: string): string | undefined {
  const match = pathname.match(/^\/products\/([^/]+)$/)
  return match ? match[1] : undefined
}

function ChatWidget() {
  const { user } = useAuth()
  const location = useLocation()
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([GREETING])
  const [input, setInput] = useState('')
  const [isSending, setIsSending] = useState(false)
  const [productsById, setProductsById] = useState<Record<string, ProductDetail>>({})
  const bodyRef = useRef<HTMLDivElement>(null)

  async function loadProducts(ids: string[]) {
    const newIds = ids.filter((id) => !(id in productsById))
    if (newIds.length === 0) return
    const fetched = await Promise.all(
      newIds.map(async (id) => {
        try {
          return [id, await fetchProduct(id)] as const
        } catch {
          return null
        }
      }),
    )
    setProductsById((prev) => {
      const next = { ...prev }
      for (const entry of fetched) {
        if (entry) next[entry[0]] = entry[1]
      }
      return next
    })
  }

  // Reload this shopper's saved history when they log in; reset to a fresh
  // guest greeting when they log out (don't carry a previous account's chat
  // into a new guest session).
  useEffect(() => {
    if (!user) {
      setMessages([GREETING])
      return
    }

    let cancelled = false
    fetchChatHistory(user.id)
      .then((history) => {
        if (cancelled) return
        if (history.length === 0) {
          setMessages([GREETING])
          return
        }
        setMessages(
          history.map((h) => ({
            role: h.role,
            text: h.content,
            productIds: h.product_ids.length > 0 ? h.product_ids : undefined,
          })),
        )
        const allIds = history.flatMap((h) => h.product_ids)
        if (allIds.length > 0) loadProducts(allIds)
      })
      .catch(() => {
        // keep the default greeting if history fails to load
      })

    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user])

  // Keep the newest message in view instead of leaving shoppers to scroll
  // down manually after every reply.
  useEffect(() => {
    bodyRef.current?.scrollTo({ top: bodyRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, isSending])

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    const message = input.trim()
    if (!message || isSending) return

    setMessages((prev) => [...prev, { role: 'user', text: message }])
    setInput('')
    setIsSending(true)
    try {
      const currentProductId = getCurrentProductId(location.pathname)
      const result = await sendChatMessage(message, { userId: user?.id, currentProductId })
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', text: result.reply, productIds: result.mentioned_product_ids },
      ])
      await loadProducts(result.mentioned_product_ids)
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: err instanceof Error ? err.message : "Sorry, something went wrong. Please try again.",
        },
      ])
    } finally {
      setIsSending(false)
    }
  }

  return (
    <div className="chat-widget">
      {isOpen && (
        <div className="chat-widget__panel">
          <div className="chat-widget__header">
            <span>Campus Customs Chat</span>
            <button
              type="button"
              className="chat-widget__close"
              onClick={() => setIsOpen(false)}
              aria-label="Close chat"
            >
              ×
            </button>
          </div>
          <div className="chat-widget__body" ref={bodyRef}>
            {messages.map((m, i) => (
              <div key={i}>
                <p className={`chat-message chat-message--${m.role}`}>{m.text}</p>
                {m.productIds && m.productIds.length > 0 && (
                  <div className="chat-product-list">
                    {m.productIds.map((id) => {
                      const product = productsById[id]
                      if (!product) return null
                      return (
                        <Link key={id} to={`/products/${id}`} className="chat-product-card">
                          <img src={mediaUrl(product.image_url)} alt={product.name} />
                          <div className="chat-product-card__body">
                            <p className="chat-product-card__name">{product.name}</p>
                            <p className="chat-product-card__price">${product.price.toFixed(2)}</p>
                            <p className="chat-product-card__description">
                              {truncate(product.description)}
                            </p>
                          </div>
                        </Link>
                      )
                    })}
                  </div>
                )}
              </div>
            ))}
            {isSending && <p className="chat-message chat-message--assistant">Thinking...</p>}
          </div>
          <form className="chat-widget__input-row" onSubmit={handleSubmit}>
            <input
              type="text"
              placeholder="Ask about our gear..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isSending}
            />
            <button type="submit" disabled={isSending || !input.trim()}>
              Send
            </button>
          </form>
        </div>
      )}
      <button
        type="button"
        className="chat-widget__toggle"
        onClick={() => setIsOpen((open) => !open)}
        aria-label="Toggle chat"
      >
        {isOpen ? 'Close' : 'Chat'}
      </button>
    </div>
  )
}

export default ChatWidget
