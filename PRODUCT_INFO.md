# WasteWise - Product Identification Guide

## Product Overview

**Name:** WasteWise  
**Version:** 1.0.0  
**Description:** Premium eco-app for waste classification, carbon tracking, and green rewards  
**Team:** WasteWise Team  
**Homepage:** https://wastewise.eco  
**License:** MIT

---

## Product Identification Across the Codebase

### Frontend Identification

#### Package Metadata (`cinematic-scroll/package.json`)
```json
{
  "name": "wastewise-frontend",
  "version": "1.0.0",
  "description": "WasteWise - Premium eco-app for waste classification, carbon tracking, and green rewards"
}
```

#### HTML Pages
- **index.html**: Title: "WasteWise — A Greener Future"
- **dashboard.html**: Title: "WasteWise — Dashboard"
- **ai-chat.html**: Title: "WasteWise AI — Chat"
- **home.html**: References to "WasteWise features"
- **shop.html**: Links labeled "WasteWise"

---

### Backend Identification

#### Product Constants (`backend/config.py`)
```python
PRODUCT_NAME = "WasteWise"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Premium eco-app for waste classification, carbon tracking, and green rewards"
APP_AUTHOR = "WasteWise Team"
APP_HOMEPAGE = "https://wastewise.eco"
```

#### Package Initialization (`backend/__init__.py`)
```python
__version__ = "1.0.0"
__title__ = "WasteWise"
__description__ = "Premium eco-app for waste classification, carbon tracking, and green rewards"
__author__ = "WasteWise Team"
```

#### API Documentation
- **Endpoint**: FastAPI with Swagger UI at `/docs`
- **API Title**: "WasteWise API"
- **API Description**: "Premium eco-app for waste classification, carbon tracking, and green rewards"
- **API Version**: 1.0.0

---

### Deployment & Infrastructure

#### Docker Configuration (`Dockerfile`)

Metadata labels:
```dockerfile
LABEL org.opencontainers.image.title="WasteWise"
LABEL org.opencontainers.image.description="Premium eco-app for waste classification, carbon tracking, and green rewards"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.authors="WasteWise Team"
```

#### Docker Compose (`docker-compose.yml`)

Service labels:
```yaml
labels:
  - "app.name=WasteWise"
  - "app.description=Premium eco-app for waste classification, carbon tracking, and green rewards"
  - "app.version=1.0.0"
  - "app.author=WasteWise Team"
```

#### Environment Configuration (`.env.example`)
```
# ===== WASTEWISE APPLICATION CONFIGURATION =====
# Product: WasteWise - Premium eco-app for waste classification, carbon tracking, and green rewards
# Version: 1.0.0
# Team: WasteWise Team
```

---

### Documentation

- **README.md**: Product name and clear project description
- **IMPROVEMENTS.md**: Refers to "WasteWise Code Improvements"
- **PRODUCT_INFO.md**: This file - comprehensive product identification guide

---

## Usage Examples

### Accessing Product Information in Python

```python
from backend import __version__, __title__
from backend.config import PRODUCT_NAME, APP_VERSION, APP_DESCRIPTION

print(f"Product: {PRODUCT_NAME} v{APP_VERSION}")
print(f"Description: {APP_DESCRIPTION}")
```

### Docker Image Inspection

```bash
# View product metadata in Docker image
docker inspect wastewise | grep -A 5 "Labels"
```

### API Documentation

Visit http://localhost:8000/docs to see:
- API Title: "WasteWise API"
- Full API documentation with product branding

---

## Naming Conventions

- **Product Name**: WasteWise (CamelCase with capital W)
- **Docker Image**: wastewise (lowercase, no spaces)
- **Python Package**: wastewise (lowercase, can use hyphens or underscores for multi-word modules)
- **Git Repository**: waste-wise- (with hyphens for readability)
- **Service Name**: wastewise-app (in Docker Compose)

---

## Version Management

All version information is centralized in:
1. `backend/config.py` - `APP_VERSION`
2. `backend/__init__.py` - `__version__`
3. `cinematic-scroll/package.json` - `version` field
4. Dockerfile - Label version
5. Docker Compose - Label version
6. `.env.example` - Comment documentation

When updating the version, update all these locations to maintain consistency.

---

## Branding Elements

- **Primary Color**: Green (ecological theme)
- **Secondary Color**: Gray (professional)
- **Tagline**: "A Greener Future"
- **Emoji**: 🌱 (seedling)
- **Target Audience**: Environmentally conscious users focused on waste management

---

## Related Documentation

- [README.md](../README.md) - Main project documentation
- [IMPROVEMENTS.md](../IMPROVEMENTS.md) - Code quality improvements
- [ISSUES_FIXED.md](../ISSUES_FIXED.md) - Issue tracking
