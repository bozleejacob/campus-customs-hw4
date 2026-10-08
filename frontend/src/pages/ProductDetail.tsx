import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { fetchProduct, mediaUrl, type ProductDetail as ProductDetailType } from '../api'

function ProductDetail() {
  const { productId } = useParams<{ productId: string }>()
  const [product, setProduct] = useState<ProductDetailType | null>(null)
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading')

  useEffect(() => {
    if (!productId) return
    setStatus('loading')
    fetchProduct(productId)
      .then((data) => {
        setProduct(data)
        setStatus('ready')
      })
      .catch(() => setStatus('error'))
  }, [productId])

  if (status === 'loading') {
    return (
      <div className="page page--product-detail">
        <p>Loading product...</p>
      </div>
    )
  }

  if (status === 'error' || !product) {
    return (
      <div className="page page--product-detail">
        <p>We couldn't find that product.</p>
        <Link to="/products">Back to Products</Link>
      </div>
    )
  }

  return (
    <div className="page page--product-detail">
      <Link to="/products" className="back-link">
        ← Back to Products
      </Link>
      <div className="product-detail">
        <div className="product-detail__image">
          <img src={mediaUrl(product.image_url)} alt={product.name} />
        </div>
        <div className="product-detail__info">
          <h1>{product.name}</h1>
          <p className="product-detail__price">${product.price.toFixed(2)}</p>
          <p className="product-detail__description">{product.description}</p>

          <h2>Colors</h2>
          <p>{product.colors.join(', ')}</p>

          <h2>Sizes &amp; Stock</h2>
          <ul className="size-stock-list">
            {product.sizes.map((s) => (
              <li key={s.size}>
                <span className="size-stock-list__size">{s.size}</span>
                <span className={s.quantity > 0 ? 'in-stock' : 'out-of-stock'}>
                  {s.quantity > 0 ? `${s.quantity} in stock` : 'Out of stock'}
                </span>
              </li>
            ))}
          </ul>
          <p className="product-detail__total-stock">
            Total stock: {product.total_stock} units
          </p>
        </div>
      </div>
    </div>
  )
}

export default ProductDetail
