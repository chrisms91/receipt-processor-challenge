# fetch-receipt-processor-challenge

This repository contains my solution for the **Receipt Processor Challenge** – a take-home exercise for a Backend Engineer opportunity at Fetch. The goal of this challenge is to build a documented API that processes receipt data, calculates reward points based on a set of business rules, and exposes endpoints to both process receipts and retrieve their computed scores.

For more details on the challenge, please refer to the [Fetch Rewards Receipt Processor Challenge repository](https://github.com/fetch-rewards/receipt-processor-challenge/tree/main).

## Running the Project

Run the following commands:

```bash
# Clone the repository
git clone git@github.com:chrisms91/receipt-processor-challenge.git
cd receipt-processor-challenge

# Start the Docker container
docker-compose up api
```

To test the API, use `curl` or a browser.

### **POST /receipts/process**
Submit a receipt for processing:

```bash
curl -X POST http://localhost:8080/receipts/process \
     -H "Content-Type: application/json" \
     -d '{
         "retailer": "M&M Corner Market",
         "purchaseDate": "2022-03-20",
         "purchaseTime": "14:33",
         "items": [
             { "shortDescription": "Gatorade", "price": "2.25" },
             { "shortDescription": "Gatorade", "price": "2.25" },
             { "shortDescription": "Gatorade", "price": "2.25" },
             { "shortDescription": "Gatorade", "price": "2.25" }
         ],
         "total": "9.00"
     }'
```

**Example Response:**
```json
{
    "id": "bb4f4576-28b6-4655-9faf-3f39fd0f9fe4"
}
```

### **GET /receipts/{id}/points**
Retrieve the points for a processed receipt by using the returned `id`:

```bash
curl -X GET http://localhost:8080/receipts/bb4f4576-28b6-4655-9faf-3f39fd0f9fe4/points
```

Alternatively, open the following URL in your browser:
```
http://localhost:8080/receipts/{returned_id}/points
```

**Example Response:**
```json
{
    "points": 109
}
```

## Running Tests
Run the following command to execute unit tests:

```bash
docker-compose run --rm tests
```

This will execute the test suite, validating API functionality.