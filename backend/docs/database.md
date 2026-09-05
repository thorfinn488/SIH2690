# SIH 26090 - Database Schema Documentation

The database schema consists of **11 tables** designed for high modularity, transactional consistency, and strict referential integrity.

---

## Entity Relationship Summary

```
                       +-------------------+
                       |       users       |
                       +-------------------+
                       | id (UUID PK)      |
                       | name, phone       |
                       | password_hash     |
                       | role (Enum)       |
                       +---------+---------+
                                 |
         +-----------------------+-----------------------+
         | 1:1                                           | 1:1
+--------v----------+                           +--------v----------+
|     artisans      |                           |      buyers       |
+-------------------+                           +-------------------+
| id (UUID PK)      |                           | id (UUID PK)      |
| user_id (FK)      |                           | user_id (FK)      |
| region, specialty |                           | company_name      |
+--------+----------+                           +--------+----------+
         |                                               |
         | 1:N                                           | 1:N
+--------v----------+                           |
|     products      |                           |
+-------------------+                           |
| id (UUID PK)      |                           |
| artisan_id (FK)   |                           |
| status (Enum)     |                           |
+----+----+----+----+                           |
     |    |    |                                |
  1:N| 1:1| 1:1| 1:N                            |
     |    |    +------------+                   |
     |    |                 |                   |
+----v--+ |           +-----v-----+      +------v------------+
|images | |           | catalogues|      |market_opportunities|
+-------+ |           +-----------+      +-------------------+
          |                              | product_id (FK)   |
       +--v-----+                        | buyer_id (FK)     |
       | pricing|                        | match_score       |
       +--------+                        +-------------------+
```

---

## Detailed Table Specifications

### 1. `users`
- `id` (UUID, Primary Key)
- `name` (VARCHAR(255), Not Null)
- `phone` (VARCHAR(50), Unique, Index, Not Null)
- `password_hash` (VARCHAR(255), Not Null)
- `role` (ENUM: `ARTISAN`, `ADMIN`, `BUYER`, Not Null)
- `created_at` (TIMESTAMP WITH TIMEZONE, Not Null)

### 2. `artisans`
- `id` (UUID, Primary Key)
- `user_id` (UUID, FK -> `users.id` ON DELETE CASCADE, Unique, Not Null)
- `region` (VARCHAR(255), Not Null)
- `craft_specialty` (VARCHAR(255), Not Null)
- `created_at` (TIMESTAMP WITH TIMEZONE, Not Null)

### 3. `buyers`
- `id` (UUID, Primary Key)
- `user_id` (UUID, FK -> `users.id` ON DELETE CASCADE, Unique, Not Null)
- `company_name` (VARCHAR(255), Not Null)
- `requirements` (TEXT, Nullable)
- `created_at` (TIMESTAMP WITH TIMEZONE, Not Null)

### 4. `products`
- `id` (UUID, Primary Key)
- `artisan_id` (UUID, FK -> `artisans.id` ON DELETE CASCADE, Index, Not Null)
- `status` (ENUM: `DRAFT`, `PROCESSING`, `READY`, `PUBLISHED`, `FAILED`, Not Null)
- `processing_step` (VARCHAR(100), Default: `"idle"`)
- `processing_progress` (INTEGER, Default: `0`)
- `error_message` (VARCHAR(500), Nullable)
- `created_at` (TIMESTAMP WITH TIMEZONE, Not Null)
- `updated_at` (TIMESTAMP WITH TIMEZONE, Not Null)

### 5. `product_images`
- `id` (UUID, Primary Key)
- `product_id` (UUID, FK -> `products.id` ON DELETE CASCADE, Index, Not Null)
- `url` (VARCHAR(1024), Not Null)
- `uploaded_at` (TIMESTAMP WITH TIMEZONE, Not Null)

### 6. `product_audio`
- `id` (UUID, Primary Key)
- `product_id` (UUID, FK -> `products.id` ON DELETE CASCADE, Index, Not Null)
- `url` (VARCHAR(1024), Not Null)
- `uploaded_at` (TIMESTAMP WITH TIMEZONE, Not Null)

### 7. `catalogues`
- `id` (UUID, Primary Key)
- `product_id` (UUID, FK -> `products.id` ON DELETE CASCADE, Unique, Index, Not Null)
- `name` (VARCHAR(255), Not Null)
- `category` (VARCHAR(255), Not Null)
- `material` (VARCHAR(255), Not Null)
- `craft` (VARCHAR(255), Not Null)
- `description` (TEXT, Not Null)
- `tags` (JSON / Array of Strings)
- `created_at` (TIMESTAMP WITH TIMEZONE, Not Null)
- `updated_at` (TIMESTAMP WITH TIMEZONE, Not Null)

### 8. `pricing`
- `id` (UUID, Primary Key)
- `product_id` (UUID, FK -> `products.id` ON DELETE CASCADE, Unique, Index, Not Null)
- `suggested_price` (FLOAT / NUMERIC, Not Null)
- `price_range_low` (FLOAT / NUMERIC, Not Null)
- `price_range_high` (FLOAT / NUMERIC, Not Null)
- `explanation` (TEXT, Not Null)

### 9. `market_opportunities`
- `id` (UUID, Primary Key)
- `product_id` (UUID, FK -> `products.id` ON DELETE CASCADE, Index, Not Null)
- `buyer_id` (UUID, FK -> `buyers.id` ON DELETE CASCADE, Index, Not Null)
- `match_score` (INTEGER, Not Null)
- `status` (ENUM: `OPEN`, `CONTACTED`, `CLOSED`, Not Null)
- `created_at` (TIMESTAMP WITH TIMEZONE, Not Null)

### 10. `ai_insights`
- `id` (UUID, Primary Key)
- `artisan_id` (UUID, FK -> `artisans.id` ON DELETE CASCADE, Index, Not Null)
- `type` (VARCHAR(100), Not Null)
- `message` (TEXT, Not Null)
- `created_at` (TIMESTAMP WITH TIMEZONE, Not Null)

### 11. `audit_logs`
- `id` (UUID, Primary Key)
- `user_id` (UUID, FK -> `users.id` ON DELETE SET NULL, Index, Nullable)
- `action` (VARCHAR(255), Not Null)
- `timestamp` (TIMESTAMP WITH TIMEZONE, Not Null)
- `metadata` (JSON, Nullable)
