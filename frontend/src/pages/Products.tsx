import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchProducts, mediaUrl, type ProductSummary } from '../api'

function Products() {
  const [products, setProducts] = useState<ProductSummary[]>([])
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading')

  useEffect(() => {
    fetchProducts()
      .then((data) => {
        setProducts(data)
        setStatus('ready')
      })
      .catch(() => setStatus('error'))
  }, [])

  if (status === 'loading') {
    return (
      <div className="page page--products">
        <h1>Products</h1>
        <p>Loading products...</p>
      </div>
    )
  }

  if (status === 'error') {
    return (
      <div className="page page--products">
        <h1>Products</h1>
        <p>Couldn't load products right now. Is the backend API running on port 8000?</p>
      </div>
    )
  }

  return (
    <div className="page page--products">
      <h1>Products</h1>
      <div className="product-grid">
        {products.map((product) => (
          <Link
            key={product.product_id}
            to={`/products/${product.product_id}`}
            className="product-card"
          >
            <img src={mediaUrl(product.image_url)} alt={product.name} />
            <div className="product-card__body">
              <h2>{product.name}</h2>
              <p className="product-card__price">${product.price.toFixed(2)}</p>
              <p className="product-card__description">{product.short_description}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}

export default Products
