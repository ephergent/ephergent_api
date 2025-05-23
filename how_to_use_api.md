# 📬 How to Use the API Locally for Testing

This guide walks you through interacting with the local Mail API.

---

## 🔍 List All Subscribers (GET)

No authentication required.

```bash
curl -X GET "https://api.ephergent.com//api/v1/mail/subscribers/"
```

---

## ➕ Add a Subscriber (POST)

### 1. Generate the Timestamp

```bash
TIMESTAMP=$(date +%s)
```

### 2. Define the Action

```bash
ACTION="subscribe-add"
```

### 3. Calculate the Signature

Replace `YOUR_API_SECRET` with your actual API secret:

```bash
API_SECRET="YOUR_API_SECRET"
SIGNATURE=$(echo -n "${TIMESTAMP}${ACTION}" | openssl dgst -sha256 -hmac "${API_SECRET}" | cut -d ' ' -f2)
```

### 4. Make the API Call

```bash
curl -X POST "https://api.ephergent.com//api/v1/mail/subscribers/" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "address=beforegr8ness@gmail.com"
```

---

## 📄 Get Subscriber Details (GET)

No authentication required.

```bash
curl -X GET "https://api.ephergent.com//api/v1/mail/subscribers/beforegr8ness@gmail.com"
```

---

## ✏️ Update a Subscriber (PUT)

### 1. Generate the Timestamp

```bash
TIMESTAMP=$(date +%s)
```

### 2. Define the Action

```bash
ACTION="subscribe-update"
```

### 3. Calculate the Signature

```bash
API_SECRET="YOUR_API_SECRET"
SIGNATURE=$(echo -n "${TIMESTAMP}${ACTION}" | openssl dgst -sha256 -hmac "${API_SECRET}" | cut -d ' ' -f2)
```

### 4. Make the API Call

```bash
curl -X PUT "https://api.ephergent.com//api/v1/mail/subscribers/beforegr8ness@gmail.com" \
    -H "X-Timestamp: ${TIMESTAMP}" \
    -H "X-Signature: ${SIGNATURE}" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "name=Before%20Greatness"
```

---

## ❌ Delete a Subscriber (DELETE)

### 1. Generate the Timestamp

```bash
TIMESTAMP=$(date +%s)
```

### 2. Define the Action

```bash
ACTION="subscribe-delete"
```

### 3. Calculate the Signature

```bash
API_SECRET="YOUR_API_SECRET"
SIGNATURE=$(echo -n "${TIMESTAMP}${ACTION}" | openssl dgst -sha256 -hmac "${API_SECRET}" | cut -d ' ' -f2)
```

### 4. Make the API Call

```bash
curl -X DELETE "https://api.ephergent.com//api/v1/mail/subscribers/jeremy.schroeder@proton.me" \
    -H "X-Timestamp: ${TIMESTAMP}" \
    -H "X-Signature: ${SIGNATURE}"
```
jeremy.schroeder@proton.me