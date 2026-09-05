# SIH 26090 - API Specification

All API responses strictly adhere to the unified response envelope format:

### Standard Success Response Envelope
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

### Standard Error Response Envelope
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error description"
  }
}
```

### Standard Error Codes
- `FILE_TOO_LARGE` (400)
- `INVALID_FILE_TYPE` (400)
- `VALIDATION_ERROR` (400 / 422)
- `UNAUTHORIZED` (401)
- `FORBIDDEN` (403)
- `NOT_FOUND` (404)
- `RATE_LIMIT_EXCEEDED` (429)
- `AI_PROCESSING_FAILED` (500)
- `INTERNAL_ERROR` (500)

---

## Auth Endpoints (`/api/auth`)

### 1. Register User
`POST /api/auth/register`
**Request Body**:
```json
{
  "name": "Sunita Devi",
  "phone": "9811122233",
  "password": "SecretPassword123",
  "role": "ARTISAN",
  "region": "Patiala, Punjab",
  "craft_specialty": "Phulkari Embroidery"
}
```
**Response**:
```json
{
  "success": true,
  "data": {
    "user_id": "c1f7b8e2-...",
    "name": "Sunita Devi",
    "role": "ARTISAN",
    "token": "eyJhbGciOi..."
  },
  "error": null
}
```

### 2. Login User
`POST /api/auth/login`
**Request Body**:
```json
{
  "phone": "9811122233",
  "password": "SecretPassword123"
}
```
**Response**:
```json
{
  "success": true,
  "data": {
    "user_id": "c1f7b8e2-...",
    "name": "Sunita Devi",
    "role": "ARTISAN",
    "token": "eyJhbGciOi..."
  },
  "error": null
}
```

### 3. Get Current User Profile
`GET /api/auth/me`
**Headers**: `Authorization: Bearer <token>`
**Response**:
```json
{
  "success": true,
  "data": {
    "user_id": "c1f7b8e2-...",
    "name": "Sunita Devi",
    "role": "ARTISAN",
    "phone": "9811122233"
  },
  "error": null
}
```

---

## Products Endpoints (`/api/products`)

### 1. Create Product
`POST /api/products` (Auth: `ARTISAN`, `ADMIN`)
**Response**:
```json
{
  "success": true,
  "data": {
    "product_id": "p001-...",
    "status": "DRAFT"
  },
  "error": null
}
```

### 2. Upload Product Image
`POST /api/products/{id}/image` (Auth: `ARTISAN`, `ADMIN`)
**Content-Type**: `multipart/form-data` (`file`)
**Response**:
```json
{
  "success": true,
  "data": {
    "product_id": "p001-...",
    "image_url": "/static/uploads/a1b2c3d4.jpg"
  },
  "error": null
}
```

### 3. Upload Product Audio
`POST /api/products/{id}/audio` (Auth: `ARTISAN`, `ADMIN`)
**Content-Type**: `multipart/form-data` (`file`)
**Response**:
```json
{
  "success": true,
  "data": {
    "product_id": "p001-...",
    "audio_url": "/static/uploads/a1b2c3d4.mp3"
  },
  "error": null
}
```

### 4. Trigger AI Pipeline Processing
`POST /api/products/{id}/process` (Auth: `ARTISAN`, `ADMIN`)
**Response**:
```json
{
  "success": true,
  "data": {
    "product_id": "p001-...",
    "status": "PROCESSING",
    "job_id": "job_p001-..."
  },
  "error": null
}
```

### 5. Poll Processing Status
`GET /api/products/{id}/processing-status` (Auth: Required)
**Response**:
```json
{
  "success": true,
  "data": {
    "product_id": "p001-...",
    "status": "PROCESSING",
    "step": "generating_catalogue",
    "progress_percent": 55
  },
  "error": null
}
```

### 6. Get Product Details
`GET /api/products/{id}` (Auth: Required)
**Response**:
```json
{
  "success": true,
  "data": {
    "id": "p001-...",
    "artisan_id": "art001-...",
    "status": "READY",
    "created_at": "2026-09-05T10:00:00Z",
    "images": [{"id": "img1", "url": "/static/uploads/sample.jpg"}],
    "audio": [],
    "catalogue": {
      "id": "cat1",
      "product_id": "p001-...",
      "name": "Handcrafted Phulkari Silk Embroidery Dupatta",
      "category": "Textiles & Apparel",
      "material": "Pure Cotton with Silk Embroidery",
      "craft": "Phulkari",
      "description": "Authentic traditional Phulkari dupatta...",
      "tags": ["phulkari", "silk", "handwoven"]
    },
    "pricing": {
      "id": "pr1",
      "product_id": "p001-...",
      "suggested_price": 2380.0,
      "price_range_low": 2140.0,
      "price_range_high": 2740.0,
      "explanation": "The recommended price of ₹2,380..."
    },
    "opportunities": [
      {
        "buyer_name": "FabIndia Retail Ltd.",
        "match_score": 95,
        "location": "India",
        "requirement": "Bulk requirement of 50 hand-embroidered silk dupattas."
      }
    ]
  },
  "error": null
}
```

### 7. Update Product Catalogue
`PUT /api/products/{id}/catalogue` (Auth: `ARTISAN`, `ADMIN`)
**Request Body**:
```json
{
  "name": "Updated Phulkari Dupatta",
  "description": "Updated artisan description"
}
```
**Response**:
```json
{
  "success": true,
  "data": {
    "product_id": "p001-...",
    "updated": true
  },
  "error": null
}
```

### 8. List Products
`GET /api/products?page=1&page_size=10` (Auth: Required)

### 9. Delete Product
`DELETE /api/products/{id}` (Auth: `ARTISAN`, `ADMIN`)

---

## Dashboard Endpoints (`/api/dashboard`)

### 1. Get Artisan Dashboard Summary
`GET /api/dashboard` (Auth: `ARTISAN`)
**Response**:
```json
{
  "success": true,
  "data": {
    "total_products": 3,
    "catalogue_status": {
      "ready": 2,
      "processing": 0,
      "draft": 1
    },
    "recent_products": [ ... ]
  },
  "error": null
}
```

### 2. Get AI Insights
`GET /api/dashboard/insights` (Auth: `ARTISAN`)
**Response**:
```json
{
  "success": true,
  "data": {
    "insights": [
      {
        "type": "MARKET_DEMAND",
        "message": "High demand detected for Phulkari embroidery dupattas."
      }
    ]
  },
  "error": null
}
```

---

## Admin Endpoints (`/api/admin`)

- `GET /api/admin/artisans` (Auth: `ADMIN`)
- `GET /api/admin/products` (Auth: `ADMIN`)
- `GET /api/admin/opportunities` (Auth: `ADMIN`)
