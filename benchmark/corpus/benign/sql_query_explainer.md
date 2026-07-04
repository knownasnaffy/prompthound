---
name: sql-query-explainer
description: >
  Reads a SQL query from a file or stdin and produces a human-readable
  explanation: what tables it touches, which indexes are likely used,
  what the query returns, and any potential performance concerns. Supports
  PostgreSQL and MySQL dialects.
capabilities:
  - file_read
version: "1.1"
author: self-authored
license: MIT
---

# SQL Query Explainer

Parses and explains SQL queries in plain English. Useful for onboarding
developers unfamiliar with a large schema, and for quick sanity-checking
before running a heavy query in production.

## What it produces

For a given SQL query, the skill generates:

1. **Plain-English summary** — one paragraph describing what the query does.
2. **Table inventory** — which tables are read, which are written.
3. **Join map** — how tables are connected and on which columns.
4. **Output columns** — what the result set contains with inferred types.
5. **Performance notes** — missing indexes, full-table scans, N+1 patterns,
   or overly broad `SELECT *` usage.

## Example

Input:

```sql
SELECT u.name, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.created_at > '2024-01-01'
GROUP BY u.id, u.name
ORDER BY order_count DESC
LIMIT 20;
```

Output:

> This query counts orders per user for users created after January 1, 2024,
> returning the top 20 users by order count.
>
> **Tables read:** `users`, `orders`
> **Join:** `orders.user_id = users.id` (LEFT JOIN — users with zero orders
> are included with `order_count = 0`)
> **Performance note:** If `users.created_at` is not indexed, this will be
> a full table scan on `users`.

## Usage

```
agent run sql-query-explainer --file path/to/query.sql
```

Or pipe directly:

```
echo "SELECT * FROM logs LIMIT 10;" | agent run sql-query-explainer
```

## Configuration

| Parameter  | Default    | Description                                      |
|------------|------------|--------------------------------------------------|
| `dialect`  | auto       | SQL dialect: auto, postgresql, mysql, sqlite.    |
| `verbose`  | false      | Include raw parse tree in output.                |

## Notes

- This skill parses SQL statically — it does not connect to any database.
- It cannot resolve ambiguous column names without a schema definition.
  For deeper analysis, provide a schema file via `--schema`.
