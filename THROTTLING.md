# API Throttling Configuration

This document explains the throttling limits implemented in the Task Management API to prevent abuse and ensure fair usage.

## Overview

The API uses Django REST Framework's throttling system with custom throttle classes to control request rates across different endpoints and user types.

## Throttle Rates

### Default Rates
- **Anonymous Users**: 100 requests/hour
- **Authenticated Users**: 1000 requests/hour

### Specific Endpoint Rates

#### Authentication Endpoints
- **Login (`/api/auth/login/`)**: 10 attempts/hour per IP
- **Registration (`/api/auth/register/`)**: 5 registrations/hour per IP
- **Token Refresh (`/api/auth/refresh/`)**: 50 requests/hour per user
- **Password Reset**: 3 requests/hour per IP

#### Task Management Endpoints
- **Task Creation**: 100 tasks/hour per user
- **Task Updates**: 200 updates/hour per user
- **Task Listing/Reading**: 2000 requests/hour per user
- **Task Statistics**: 2000 requests/hour per user

#### User Profile Endpoints
- **Profile Access (`/api/auth/me/`)**: 500 requests/hour per user
- **Logout**: 500 requests/hour per user

### Security Levels

#### Low Security (Reading Operations)
- **Rate**: 2000 requests/hour
- **Endpoints**: Task statistics, profile reading
- **Purpose**: Allow frequent reading of non-sensitive data

#### Medium Security (Standard Operations)
- **Rate**: 500 requests/hour
- **Endpoints**: Profile access, logout, general user operations
- **Purpose**: Normal user operations with reasonable limits

#### High Security (Sensitive Operations)
- **Rate**: 50 requests/hour
- **Endpoints**: Token refresh, password changes
- **Purpose**: Strict limits on security-sensitive operations

### Burst Protection
- **Rate**: 60 requests/minute
- **Purpose**: Prevents rapid-fire attacks
- **Applied to**: All authentication and task modification endpoints

### Daily Limits
- **Rate**: 1000 requests/day per user
- **Purpose**: Overall usage cap to prevent system abuse
- **Scope**: Applies to authenticated users across all endpoints

## Admin Users

Admin users automatically receive 5x higher limits for most operations:
- Standard user rate × 5 for most endpoints
- Helps with administrative tasks and monitoring

## Throttle Classes

### Custom Throttle Classes

1. **LoginRateThrottle**: Prevents brute force login attempts
2. **RegisterRateThrottle**: Prevents spam user registration
3. **TaskCreateRateThrottle**: Limits task creation
4. **TaskUpdateRateThrottle**: Limits task modifications
5. **BurstRateThrottle**: General rapid-fire protection
6. **HighSecurityThrottle**: For sensitive operations
7. **MediumSecurityThrottle**: For standard operations
8. **LowSecurityThrottle**: For reading operations

## How Throttling Works

### Rate Calculation
- Rates are calculated per IP address for anonymous users
- Rates are calculated per user ID for authenticated users
- Sliding window approach (not fixed time periods)

### Response Headers
When throttled, the API returns:
- **Status Code**: 429 (Too Many Requests)
- **Header**: `Retry-After` (seconds until next request allowed)
- **Message**: Information about rate limit exceeded

### Example Response
```json
{
    "detail": "Request was throttled. Expected available in 3600 seconds."
}
```

## Security Benefits

### Brute Force Protection
- Login throttling prevents password guessing attacks
- Registration throttling prevents spam account creation

### DoS Protection
- Burst protection prevents rapid request flooding
- Daily limits prevent sustained abuse

### Resource Conservation
- Limits prevent excessive database queries
- Helps maintain system performance for all users

### Fair Usage
- Ensures API resources are available to all users
- Prevents any single user from monopolizing the system

## Monitoring

### Throttle Events
All throttling events are logged for monitoring:
- User ID (if authenticated)
- IP address
- Endpoint accessed
- Timestamp
- Rate limit that was exceeded

### Analytics Integration
Throttling data can be viewed in the admin analytics dashboard to identify:
- Users hitting rate limits frequently
- Endpoints under heavy load
- Potential abuse patterns

## Configuration

### Environment-Specific Rates
Different environments can have different rates:
- **Development**: More lenient for testing
- **Production**: Strict limits for security
- **Testing**: Very high limits for automated tests

### Runtime Adjustments
Rate limits can be adjusted without code changes by modifying the `DEFAULT_THROTTLE_RATES` setting in Django settings.

## Best Practices for API Consumers

### Efficient Usage
1. Cache responses when possible
2. Batch operations where supported
3. Use pagination for large datasets
4. Implement exponential backoff on 429 responses

### Error Handling
```javascript
// Example JavaScript handling
if (response.status === 429) {
    const retryAfter = response.headers.get('Retry-After');
    setTimeout(() => retryRequest(), retryAfter * 1000);
}
```

### Rate Limit Headers
Check these headers to manage your request rate:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: When the rate limit resets

## Emergency Procedures

### Temporary Rate Adjustments
In case of emergency or special events:
1. Rates can be temporarily increased via Django admin
2. Specific users can be given temporary exemptions
3. Critical endpoints can have rates adjusted independently

### Bypass for Critical Operations
Admin users have higher limits, but in emergencies:
- System administrators can bypass throttling
- Critical system operations are not throttled
- Health checks and monitoring are exempt

This throttling system ensures the API remains stable, secure, and fair for all users while preventing abuse and maintaining system performance.