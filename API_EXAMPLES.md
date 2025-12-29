# SparkAI API Endpoints - Usage Examples

## Base URL
- Local: `http://127.0.0.1:8000`
- Production: `https://your-backend-url.azurecontainerapps.io`

---

## 1. Chat Endpoint

**Endpoint:** `POST /chat`

**Description:** Main conversational chat endpoint with thread-based history.

**Request Body:**
```json
{
  "messages": ["Hello, what can you help me with?"],
  "thread_id": "unique-thread-id-123"
}
```

**Response:**
```json
"I can help you with business planning, market analysis, trade name validation, and more. What would you like to know?"
```

---

## 2. Trade Name Validation

**Endpoint:** `POST /tradename`

**Description:** Validates trade name against UAE regulations.

**Request Body:**
```json
{
  "messages": ["Check if 'Dubai Tech Solutions' is a valid trade name"],
  "thread_id": "unique-thread-id-123"
}
```

**Response:**
```json
{
  "hasNumber": false,
  "hasRegionName": true,
  "hasArabizedName": false,
  "hasGlobalName": false,
  "arabicEquivalentName": "دبي للحلول التقنية",
  "result": "Invalid",
  "remarks": "Trade name contains region name 'Dubai' which is not allowed..."
}
```

---

## 3. Executive Summary

**Endpoint:** `POST /executivesummary`

**Description:** Generates executive summary for a business concept.

**Request Body:**
```json
{
  "messages": ["Generate an executive summary for a premium coffee shop in Dubai Marina"],
  "thread_id": "unique-thread-id-123"
}
```

**Response:**
```json
{
  "summary": "Premium coffee shop offering specialty coffee...",
  "vision_analysis": "To become the leading specialty coffee destination...",
  "mission_analysis": "Provide exceptional coffee experiences..."
}
```

---

## 4. Market Analysis

**Endpoint:** `POST /marketanalysis`

**Description:** Comprehensive market analysis for specific emirate/area.

**Request Body:**
```json
{
  "industry": "Coffee Shop",
  "business_model": "Premium specialty coffee with artisanal pastries",
  "emirate": "Dubai",
  "area": "Dubai Marina",
  "language": "English"
}
```

**Response:**
```json
{
  "target_market": "Young professionals aged 25-40, expatriates with disposable income...",
  "market_size": {
    "tam": 15000000.0,
    "som": 450000.0
  },
  "competitors": [
    {
      "name": "Starbucks Dubai Marina",
      "strengths": ["Brand recognition", "Multiple locations", "Loyalty program"],
      "weaknesses": ["Standardized menu", "Higher prices", "Less artisanal"]
    },
    {
      "name": "Tom & Serg",
      "strengths": ["Artisanal quality", "Instagram-worthy", "Local favorite"],
      "weaknesses": ["Limited seating", "Long wait times", "Higher prices"]
    }
  ],
  "competitive_advantage": "Unique blend of premium quality with local flavor..."
}
```

---

## 5. Funding Requirements

**Endpoint:** `POST /fundingrequirements`

**Description:** Calculates startup and operational costs.

**Request Body:**
```json
{
  "industry": "Coffee Shop",
  "business_model": "Premium specialty coffee with artisanal pastries",
  "emirate": "Dubai",
  "area": "Dubai Marina",
  "target_market": "Young professionals aged 25-40",
  "tam": 15000000.0,
  "som": 450000.0,
  "language": "English"
}
```

**Response:**
```json
{
  "startup_costs_aed": 550000.0,
  "operational_costs_monthly_aed": 85000.0,
  "use_of_funds": "Startup costs breakdown:\n- Licensing and permits: AED 50,000..."
}
```

---

## 6. Product/Service Description ✨ NEW

**Endpoint:** `POST /productdescription`

**Description:** Generates comprehensive product/service description based on industry and business model.

**Request Body:**
```json
{
  "industry": "Coffee Shop",
  "business_model": "Premium specialty coffee with artisanal pastries",
  "language": "English"
}
```

**Response:**
```json
{
  "description": "Our premium specialty coffee shop offers an exceptional coffee experience that combines artisanal craftsmanship with modern convenience. We source single-origin beans from renowned coffee-growing regions and roast them in-house to ensure maximum freshness and flavor complexity.\n\nKey Features:\n- Specialty Coffee: Expert baristas trained in latte art and precision brewing methods\n- Artisanal Pastries: Freshly baked daily using premium ingredients\n- Comfortable Ambiance: Modern interior design with cozy seating areas\n- Premium Quality: Ethically sourced, sustainably grown coffee beans\n\nOur menu features signature drinks including pour-over coffee, cold brew, espresso-based beverages, and seasonal specialties. Each cup is crafted with attention to detail, ensuring consistency and excellence in every sip.\n\nThe pastry selection complements our coffee offerings with croissants, Danish pastries, muffins, and specialty cakes, all made from scratch by our skilled bakers.\n\nValue Proposition:\nWe provide coffee enthusiasts with a third space - a comfortable environment between home and work where they can enjoy premium coffee, connect with friends, or work remotely with reliable WiFi and charging stations.\n\nOur commitment to quality, sustainability, and customer experience sets us apart in the competitive coffee market."
}
```

**Example with Arabic:**
```json
{
  "industry": "متجر قهوة",
  "business_model": "قهوة متخصصة فاخرة مع معجنات حرفية",
  "language": "Arabic"
}
```

**Response (in Arabic):**
```json
{
  "description": "يقدم متجر القهوة المتخصص الفاخر لدينا تجربة قهوة استثنائية تجمع بين الحرفية والراحة الحديثة..."
}
```

---

## Testing the API

### Using cURL

```bash
# Test Product Description endpoint
curl -X POST "http://127.0.0.1:8000/productdescription" \
  -H "Content-Type: application/json" \
  -d '{
    "industry": "Software as a Service",
    "business_model": "B2B cloud-based CRM platform",
    "language": "English"
  }'
```

### Using Python

```python
import requests

url = "http://127.0.0.1:8000/productdescription"
payload = {
    "industry": "E-commerce",
    "business_model": "Online marketplace for local artisans",
    "language": "English"
}

response = requests.post(url, json=payload)
print(response.json()["description"])
```

### Using the Test Script

```bash
python test_productdescription.py
```

---

## Supported Languages

All endpoints that support the `language` parameter can respond in:
- English
- Arabic
- French
- Spanish
- And many others

Simply specify the desired language in the `language` field.

---

## Error Responses

**400 Bad Request:**
```json
{
  "detail": "Invalid input parameters"
}
```

**422 Unprocessable Entity:**
```json
{
  "detail": [
    {
      "loc": ["body", "industry"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error occurred"
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production deployment, consider implementing rate limiting based on your Azure OpenAI quota.

---

## Authentication

Currently no authentication is required. For production deployment, consider implementing:
- API Keys
- OAuth 2.0
- Azure AD integration

