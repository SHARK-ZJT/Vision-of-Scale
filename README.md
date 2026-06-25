# Vision of Scale

**文生图应用 — 巨构与人的对比 | Megastructure vs Human Scale**

A text-to-image generation web app themed around *megastructures* — vast, awe-inspiring architectures that dwarf the human figures placed beside them. Powered by 火山引擎 即梦AI (Seedream) Image Generation 4.0.

![Tech Stack](https://img.shields.io/badge/backend-FastAPI-009688?logo=fastapi)
![Python](https://img.shields.io/badge/python-3.10+-blue?logo=python)
![Database](https://img.shields.io/badge/database-SQLite-003B57?logo=sqlite)
![Frontend](https://img.shields.io/badge/frontend-HTMX_%2B_Alpine.js-3D72D7)

---

## Features

- **Text-to-Image Generation** — Describe a megastructure scene, generate 1–4 images at 1024², 16:9, or 9:16
- **Curated Prompt Library** — 24 built-in templates across 5 categories, in English and Chinese
- **Image Gallery** — Browse all generated images with infinite scroll, filtering, and lightbox view
- **Collections** — Organize generations into named collections
- **Dark-Themed UI** — Immersive dark interface with glass-morphism effects, responsive design
- **Zero Build Step** — Server-rendered HTML with HTMX + Alpine.js, no JavaScript bundler required

## Screenshots

### Generator Page
Prompt input with template sidebar, parameter controls, and live results display.

### Gallery
Masonry-style grid with infinite scroll, collection filtering, and lightbox detail view.

### Template Library
Browse 24 curated megastructure-themed prompt templates by category.

## Quick Start

### Prerequisites

- Python 3.10+
- 火山引擎方舟 API Key (via [火山引擎方舟控制台](https://console.volcengine.com/ark/))

### Setup

```bash
# 1. Clone or enter the project directory
cd "Vision of Scale"

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your ARK_API_KEY from the Volcengine Ark console

# 5. Start the server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 6. Open in browser
# http://127.0.0.1:8000
```

## Project Structure

```
Vision of Scale/
├── app/
│   ├── main.py              # FastAPI entry point, lifespan, static files
│   ├── config.py            # Environment configuration (pydantic-settings)
│   ├── dependencies.py      # Dependency injection (DB session)
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── base.py          # DeclarativeBase + init_db()
│   │   ├── generation.py    # Image generation records
│   │   ├── prompt_template.py  # Prompt templates
│   │   └── collection.py    # Image collections
│   ├── schemas/             # Pydantic request/response schemas
│   ├── routers/             # Route handlers
│   │   ├── pages.py         # HTML page routes
│   │   ├── generate.py      # POST /api/generate
│   │   ├── gallery.py       # Gallery CRUD + HTMX partials
│   │   ├── templates_api.py # Template API
│   │   └── collections_api.py  # Collection CRUD
│   ├── services/            # Business logic
│   │   ├── image_api.py     # 火山引擎方舟 (OpenAI 兼容模式)
│   │   ├── image_storage.py # Image download + thumbnail generation
│   │   └── seed_data.py     # 24 curated prompt templates
│   ├── templates/           # Jinja2 HTML templates
│   │   ├── base.html        # Root layout (nav, toast, dark theme)
│   │   ├── index.html       # Generator page
│   │   ├── gallery.html     # Gallery page
│   │   ├── template_library.html  # Template library
│   │   └── partials/        # HTMX fragment responses
│   └── static/              # CSS, JS, generated images
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## API Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Generator homepage |
| `GET` | `/gallery` | Image gallery with filters |
| `GET` | `/templates` | Prompt template library |
| `POST` | `/api/generate` | Generate images from prompt |
| `GET` | `/api/generations` | List generations (paginated) |
| `DELETE` | `/api/generations/{id}` | Delete a generation |
| `GET` | `/api/templates` | List templates |
| `GET` | `/api/collections` | List collections |
| `POST` | `/api/collections` | Create collection |

Full API docs available at `http://127.0.0.1:8000/docs` (Swagger UI) or `/redoc`.

## Prompt Template Categories

| Category | Count | Focus |
|---|---|---|
| **Megastructures** | 7 | Colossal arcologies, orbital rings, Dyson swarms, vertical cities |
| **Contrast / Scale** | 5 | Tiny humans against vast architecture, emphasis on scale |
| **Post-Human** | 3 | Nature reclaiming, abandoned megastructures, silent ruins |
| **Interiors** | 4 | Vast interior spaces, engine hearts, data cathedrals |
| **Landscapes** | 5 | Spires in deserts, floating citadels, mega-bridges |

Templates are available in both English (18) and Chinese (6).

## Tech Stack

- **Backend**: FastAPI (async), SQLAlchemy 2.0 (async ORM), SQLite via aiosqlite
- **Frontend**: Jinja2 server-rendered HTML + HTMX 2.0 + Alpine.js 3.x
- **Styling**: Tailwind CSS (CDN), custom animations
- **AI API**: 火山引擎方舟 即梦AI 4.0 (`doubao-seedream-4-0-250828`) via OpenAI SDK compatible mode

## Configuration

All configuration is via environment variables in `.env`:

```env
ARK_API_KEY=your-ark-api-key-here     # Required: Your 火山引擎 ARK API Key
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3  # API base URL
DATABASE_URL=sqlite+aiosqlite:///./vision_of_scale.db    # SQLite path
DEFAULT_MODEL=doubao-seedream-4-0-250828                  # Model name
```

## Roadmap Ideas

- [ ] User-created prompt templates
- [ ] Image-to-image / style transfer (using reference images)
- [ ] Batch generation queue
- [ ] Export collection as ZIP
- [ ] PostgreSQL migration for production
- [ ] User authentication

## License

MIT
