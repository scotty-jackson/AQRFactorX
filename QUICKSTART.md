# Quick Start Guide

Get AQR Factor Explorer running in 5 minutes!

## Prerequisites Check

```bash
# Check Python version (need 3.9+)
python --version

# Check Node.js version (need 18+)
node --version

# Check PostgreSQL is installed
psql --version
```

## Setup Steps

### 1. Database Setup (2 minutes)

```bash
# Start PostgreSQL (if not running)
# On Mac: brew services start postgresql
# On Linux: sudo service postgresql start

# Create database
psql -U postgres -c "CREATE DATABASE aqr_factors;"
psql -U postgres -c "CREATE USER aqr_user WITH PASSWORD 'aqr_password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE aqr_factors TO aqr_user;"
```

### 2. Backend Setup (2 minutes)

```bash
# Copy environment file
cp .env.example .env

# Setup Python environment
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head
```

### 3. Get Sample Data (1 minute)

Download sample AQR data:
1. Go to https://www.aqr.com/Insights/Datasets/Quality-Minus-Junk-Factors-Monthly
2. Download the CSV file
3. Save it to `data/aqr_raw/` directory

### 4. Load Data (1 minute)

```bash
# From backend directory, with venv activated
python -m backend.etl.ingest_aqr_factors --data-dir ../data/aqr_raw
```

### 5. Start Backend (30 seconds)

```bash
# From backend directory
python -m backend.main
```

Backend will run at http://localhost:8000

### 6. Start Frontend (1 minute)

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend will run at http://localhost:3000

## Verify Installation

1. Open http://localhost:3000
2. You should see the AQR Factor Explorer landing page
3. Click "Factors" to view loaded factors
4. Click on any factor to see detailed charts

## Next Steps

- Download more factor datasets from AQR
- Explore the comparison tool
- Check out the analytics dashboard
- Read the full README.md for advanced features

## Troubleshooting

**Issue**: Database connection failed
- **Fix**: Check DATABASE_URL in .env file
- **Fix**: Verify PostgreSQL is running

**Issue**: No factors showing
- **Fix**: Make sure you ran the ETL ingestion
- **Fix**: Check that CSV files are in data/aqr_raw/

**Issue**: Frontend can't connect to backend
- **Fix**: Ensure backend is running on port 8000
- **Fix**: Check NEXT_PUBLIC_API_URL in .env

## Getting Help

- Check the full README.md
- Review error logs in the terminal
- Verify all prerequisites are installed

Enjoy exploring AQR factors! 🚀
