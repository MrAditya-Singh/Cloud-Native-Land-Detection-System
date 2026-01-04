# API Documentation

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### Obtain a Token

**Endpoint:** `POST /auth/token`

**Request:**
```http
POST /api/v1/auth/token
Content-Type: application/x-www-form-urlencoded

username=your_username&password=your_password
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## User Roles

- `government`: Government agencies
- `real_estate`: Real estate firms
- `ngo`: Non-governmental organizations
- `admin`: System administrators

## Detection Types

- `encroachment`: Illegal land encroachment
- `urban_expansion`: Urban development and expansion
- `environmental_change`: Environmental changes (deforestation, water bodies, etc.)

## Severity Levels

- `Low`: Confidence 0.75-0.84
- `Medium`: Confidence 0.85-0.94
- `High`: Confidence 0.95-0.99
- `Critical`: Confidence >= 0.95 with specific conditions

## Endpoints

### Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Authentication Endpoints

#### Register User

**Endpoint:** `POST /auth/register`

**Request:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "securepassword",
  "organization": "Organization Name",
  "role": "government"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "organization": "Organization Name",
  "role": "government",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

#### Get Current User

**Endpoint:** `GET /auth/me`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "organization": "Organization Name",
  "role": "government",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

### Monitoring Region Endpoints

#### Create Monitoring Region

**Endpoint:** `POST /regions/`

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "name": "Downtown Area",
  "description": "City center monitoring",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "radius_km": 5.0
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Downtown Area",
  "description": "City center monitoring",
  "latitude": 40.7128,
  "longitude": -74.006,
  "radius_km": 5.0,
  "user_id": 1,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "last_scanned": null
}
```

#### List Monitoring Regions

**Endpoint:** `GET /regions/`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
  {
    "id": 1,
    "name": "Downtown Area",
    "description": "City center monitoring",
    "latitude": 40.7128,
    "longitude": -74.006,
    "radius_km": 5.0,
    "user_id": 1,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "last_scanned": "2024-01-05T12:00:00"
  }
]
```

#### Get Monitoring Region

**Endpoint:** `GET /regions/{region_id}`

**Headers:** `Authorization: Bearer <token>`

#### Delete Monitoring Region

**Endpoint:** `DELETE /regions/{region_id}`

**Headers:** `Authorization: Bearer <token>`

**Response:** `204 No Content`

#### Activate Region

**Endpoint:** `PUT /regions/{region_id}/activate`

**Headers:** `Authorization: Bearer <token>`

#### Deactivate Region

**Endpoint:** `PUT /regions/{region_id}/deactivate`

**Headers:** `Authorization: Bearer <token>`

### Detection Endpoints

#### Scan Region

**Endpoint:** `POST /detections/scan/{region_id}`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Scan initiated for region Downtown Area",
  "region_id": 1
}
```

#### List Detections

**Endpoint:** `GET /detections/`

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `detection_type` (optional): Filter by detection type
- `flagged_only` (optional): Show only flagged detections (boolean)

**Response:**
```json
[
  {
    "id": 1,
    "region_id": 1,
    "satellite_image_id": 1,
    "user_id": 1,
    "detection_type": "encroachment",
    "confidence_score": 0.92,
    "detected_area_sqkm": 0.5,
    "latitude": 40.7128,
    "longitude": -74.006,
    "details": {
      "encroachment_probability": 0.92,
      "confidence": 0.84
    },
    "flagged": true,
    "severity": "High",
    "created_at": "2024-01-05T12:00:00"
  }
]
```

#### Get Detection

**Endpoint:** `GET /detections/{detection_id}`

**Headers:** `Authorization: Bearer <token>`

#### Get Region Detections

**Endpoint:** `GET /detections/region/{region_id}`

**Headers:** `Authorization: Bearer <token>`

#### Analyze Region

**Endpoint:** `POST /detections/analyze`

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "region_id": 1,
  "start_date": "2024-01-01T00:00:00",
  "end_date": "2024-12-31T23:59:59",
  "detection_types": ["encroachment", "urban_expansion"]
}
```

**Response:**
```json
{
  "region_id": 1,
  "total_detections": 45,
  "encroachment_count": 12,
  "urban_expansion_count": 20,
  "environmental_change_count": 13,
  "average_confidence": 0.86,
  "flagged_count": 8,
  "detections": [...]
}
```

### Insights Endpoints

#### Get User Insights

**Endpoint:** `GET /insights/`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "total_monitored_regions": 5,
  "total_detections": 150,
  "critical_alerts": 8,
  "recent_changes": [...],
  "top_affected_regions": []
}
```

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

- `200 OK`: Success
- `201 Created`: Resource created successfully
- `202 Accepted`: Request accepted for processing
- `204 No Content`: Success with no response body
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

## Rate Limiting

Currently, there are no rate limits imposed on the API. In production, consider implementing rate limiting based on your requirements.

## Pagination

For endpoints that return lists, pagination will be added in future versions. Currently, all results are returned.

## WebSocket Support

WebSocket support for real-time updates is planned for future versions.
