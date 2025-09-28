# CLAUDE.md

## GitHub Repository Information

For sensitive credentials and detailed GitHub setup information, see `private_docs/github_credentials.md` (not tracked in version control).

## GitHub Pages Setup
- **Repository**: Public repository hosting HTML files
- **GitHub Pages URL**: External hosting for HTML documents
- **HTML Documents**: All HTML original files are hosted on GitHub Pages
- **Purpose**: Solves iframe X-Frame-Options issues by serving HTML from external domain
- **Template Integration**: Django templates use GitHub Pages URLs for iframe src attributes

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django web application called "nccjob" that manages occupational disease records and standardization. The application handles disease records, job classifications, and exposure data for occupational health analysis.

## Architecture

### Core Applications
- **records**: Main application handling disease records, case management, and revision tracking
- **dictionaries**: Contains standardized dictionaries for diseases, job codes, and exposure factors
- **core**: Django project configuration and settings

### Key Models
- **Case**: Represents individual case files identified by FID (File ID)
- **DiseaseRecord**: Central model linking cases to standardized disease, job, and exposure data
- **DiseaseDictionaryEntry**: Standardized disease names and codes
- **JobCodeOccupation**: Job classification with codes and descriptions
- **ExposureDictionary**: Standardized hazardous exposure factors
- **RecordRevision**: Tracks modification history for audit trails

### Database
- SQLite database: `nccjob_db.sqlite3`
- Uses Korean timezone (Asia/Seoul)
- Session management configured for 24-hour persistence

## Development Commands

### Environment Setup
```bash
# Activate virtual environment
source env_nccjob/bin/activate

# Install dependencies (packages are already installed in env_nccjob/)
pip install -r requirements.txt  # if requirements.txt exists
```

### Django Management
```bash
# Run development server
python manage.py runserver

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic
```

### Production Deployment
- Uses Gunicorn with systemd service: `nccjob.service`
- Runs on port 8167 with 3 workers
- Service name: `nccjob`
- Working directory: `/home/rag/papps/nccjob`
- Virtual environment: `env_nccjob/`

```bash
# Manage systemd service
sudo systemctl start nccjob
sudo systemctl stop nccjob
sudo systemctl restart nccjob
sudo systemctl status nccjob
```

## Key Configuration

### URL Structure
- Base URL prefix: `/nccjob/` (configured via FORCE_SCRIPT_NAME)
- Trusted origins: `https://sehnr.org`
- Media files served from `/data/` URL path

### Important Settings
- Debug mode: Enabled (development)
- Allowed hosts: All (`['*']`)
- Database: SQLite with custom name `nccjob_db.sqlite3`
- Session cookie name: `nccjob_sessionid`
- Media root: `data/` directory
- Static files: Collected to `staticfiles/`

## Code Conventions

### Model Field Naming
- Korean field names are used extensively in verbose_name attributes
- Field relationships follow Django conventions (ForeignKey, ManyToManyField)
- All models include proper `__str__` methods and Meta classes with Korean verbose names

### Key Relationships
- Case ↔ DiseaseRecord: One-to-many via FID
- DiseaseRecord ↔ Dictionary models: Foreign keys for standardization
- DiseaseRecord ↔ RecordRevision: One-to-many for audit trail
- User ↔ Profile: One-to-one with auto-creation via signals

### Data Integrity
- Original data preservation: All models store both current and original values
- Confirmation flags: Boolean fields track verification status for key data points
- Audit trail: RecordRevision model tracks all changes with before/after values