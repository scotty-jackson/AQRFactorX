# AQR Factor Explorer

A production-quality web application for exploring and analyzing AQR factor return data. Built with FastAPI (Python) backend and Next.js (React/TypeScript) frontend, this application provides an intuitive, interactive interface for exploring factor performance over time.

## Features

- **Interactive Factor Directory**: Browse and filter through all available AQR factors with advanced search and filtering capabilities
- **Detailed Factor Pages**: Deep dive into individual factors with cumulative return charts, rolling statistics, drawdown analysis, and performance metrics
- **Factor Comparison Tool**: Compare up to 6 factors side-by-side with synchronized charts and correlation analysis
- **Analytics Dashboard**: Discover top-performing factors across different time periods and metrics
- **Responsive Design**: Fully responsive UI that works seamlessly on desktop, tablet, and mobile devices
- **SEO Optimized**: Server-side rendering with proper meta tags for search engine visibility
- **Ad-Ready**: Placeholder containers for future monetization with Google AdSense

## Technology Stack

### Backend
- **FastAPI**: Modern, high-performance Python web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Relational database
- **Alembic**: Database migration tool
- **Pandas & NumPy**: Data processing and analytics

### Frontend
- **Next.js 14**: React framework with server-side rendering
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Recharts**: React charting library
- **Axios**: HTTP client

## Project Structure

```
AQRFactorX/
├── backend/
│   ├── alembic/              # Database migrations
│   │   └── versions/         # Migration scripts
│   ├── api/                  # API routes
│   │   ├── factors.py        # Factor endpoints
│   │   └── analytics.py      # Analytics endpoints
│   ├── etl/                  # ETL scripts
│   │   └── ingest_aqr_factors.py
│   ├── models.py             # SQLAlchemy models
│   ├── schemas.py            # Pydantic schemas
│   ├── db.py                 # Database configuration
│   ├── main.py               # FastAPI application
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── components/           # React components
│   │   ├── Layout.tsx
│   │   ├── NavBar.tsx
│   │   ├── Footer.tsx
│   │   ├── FactorCard.tsx
│   │   └── CumulativeReturnChart.tsx
│   ├── pages/                # Next.js pages
│   │   ├── index.tsx         # Landing page
│   │   ├── factors/          # Factor directory
│   │   ├── factor/[id].tsx   # Factor detail
│   │   ├── compare/          # Factor comparison
│   │   └── analytics/        # Analytics dashboard
│   ├── lib/                  # Utilities
│   │   ├── api.ts            # API client
│   │   └── utils.ts          # Helper functions
│   ├── types/                # TypeScript types
│   ├── styles/               # CSS files
│   └── package.json          # Node dependencies
├── data/
│   └── aqr_raw/              # Place AQR CSV files here
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## Prerequisites

- **Python 3.9+**
- **Node.js 18+** and npm/yarn
- **PostgreSQL 12+**
- **Git**

## Installation and Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AQRFactorX
```

### 2. Set Up PostgreSQL Database

Create a new PostgreSQL database for the application:

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE aqr_factors;
CREATE USER aqr_user WITH PASSWORD 'aqr_password';
GRANT ALL PRIVILEGES ON DATABASE aqr_factors TO aqr_user;

# Exit psql
\q
```

### 3. Configure Environment Variables

Copy the example environment file and update it with your settings:

```bash
cp .env.example .env
```

Edit `.env` and update the following:

```env
# Database Configuration
DATABASE_URL=postgresql://aqr_user:aqr_password@localhost:5432/aqr_factors

# Backend API Configuration
PORT=8000

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Set Up Backend

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head
```

### 5. Download AQR Factor Data

1. Visit [AQR Data Library](https://www.aqr.com/Insights/Datasets)
2. Download the factor datasets you're interested in (e.g., QMJ, BAB, HML Devil, Momentum, etc.)
3. Save the CSV files to the `data/aqr_raw/` directory in your project

Example datasets to download:
- Quality Minus Junk Factors
- Betting Against Beta
- The Devil in HML's Details
- Time Series Momentum
- Value and Momentum Everywhere

### 6. Ingest Factor Data

Run the ETL script to load the AQR data into your database:

```bash
# From the backend directory with virtual environment activated
python -m backend.etl.ingest_aqr_factors --data-dir ../data/aqr_raw
```

The script will:
- Parse each CSV file
- Extract factor metadata
- Compute summary statistics
- Load data into PostgreSQL
- Display progress and summary

### 7. Start the Backend Server

```bash
# From the backend directory
python -m backend.main

# Or using uvicorn directly
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API documentation (Swagger UI): `http://localhost:8000/api/docs`

### 8. Set Up Frontend

Open a new terminal window:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
# or
yarn install

# Start development server
npm run dev
# or
yarn dev
```

The frontend will be available at `http://localhost:3000`

## Usage

### Browsing Factors

1. Navigate to `http://localhost:3000`
2. Use the search bar or browse the featured factors on the landing page
3. Click "Factors" in the navigation to see all available factors
4. Use filters to narrow down by region, asset class, or frequency

### Viewing Factor Details

1. Click on any factor card to view its detail page
2. Explore cumulative returns, rolling statistics, and performance metrics
3. Adjust the rolling window and metric to analyze different aspects

### Comparing Factors

1. Click "Compare" in the navigation
2. Select 2-6 factors from the list
3. Click "Compare Factors" to see side-by-side performance
4. Review the correlation matrix to understand factor relationships

### Analytics Dashboard

1. Click "Analytics" in the navigation
2. Select a time period (last 1Y, 3Y, 5Y, 10Y, or all time)
3. Choose a ranking metric (annualized return or Sharpe ratio)
4. Optionally filter by region
5. View the podium and full rankings

## API Endpoints

### Factor Endpoints

- `GET /api/factors` - List all factors with filtering
- `GET /api/factors/{id}` - Get factor details
- `GET /api/factors/{id}/timeseries` - Get time series data
- `GET /api/factors/{id}/rolling` - Get rolling statistics
- `GET /api/factors/{id}/statistics` - Get computed statistics

### Analytics Endpoints

- `GET /api/analytics/comparison` - Compare multiple factors
- `GET /api/analytics/correlation` - Compute correlation matrix
- `GET /api/analytics/top-factors` - Get top performing factors

### Metadata Endpoints

- `GET /api/regions` - List available regions
- `GET /api/asset-classes` - List available asset classes
- `GET /api/frequencies` - List available frequencies

Full API documentation: `http://localhost:8000/api/docs`

## Data Updates

To update factor data with new observations:

1. Download the latest CSV files from AQR
2. Place them in the `data/aqr_raw/` directory
3. Run the ETL script again:

```bash
python -m backend.etl.ingest_aqr_factors --data-dir ../data/aqr_raw
```

The ETL script is idempotent and will:
- Update existing factors with new data points
- Skip duplicate observations
- Recompute summary statistics

## Production Deployment

### Backend Deployment

1. Set production environment variables
2. Use a production WSGI server (e.g., Gunicorn):

```bash
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

3. Set up a reverse proxy (nginx/Apache)
4. Configure SSL certificates
5. Set up database backups

### Frontend Deployment

1. Build the production bundle:

```bash
cd frontend
npm run build
```

2. Deploy using Vercel, Netlify, or serve with nginx:

```bash
npm run start
```

3. Update `NEXT_PUBLIC_API_URL` to point to your production API

### Database

- Set up regular backups
- Configure connection pooling
- Monitor performance and add indexes as needed
- Consider read replicas for high traffic

## Development

### Adding New Factor Datasets

To add support for new AQR datasets:

1. Add metadata to `FACTOR_METADATA` in `backend/etl/ingest_aqr_factors.py`
2. Update the ETL parsing logic if the CSV format differs
3. Run the ETL script to ingest the new data

### Adding API Endpoints

1. Add route handlers in `backend/api/`
2. Define Pydantic schemas in `backend/schemas.py`
3. Update frontend API client in `frontend/lib/api.ts`

### Styling and Theming

- Customize colors in `frontend/tailwind.config.js`
- Update global styles in `frontend/styles/globals.css`
- Modify layout components in `frontend/components/`

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running: `pg_isready`
- Check DATABASE_URL in `.env`
- Ensure database user has proper permissions

### ETL Import Errors

- Verify CSV file format matches AQR standards
- Check for empty or malformed rows
- Review ETL logs for specific error messages

### Frontend Build Errors

- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check Node.js version: `node --version` (should be 18+)
- Verify all environment variables are set

### API Connectivity Issues

- Ensure backend is running on the expected port
- Check CORS configuration in `backend/main.py`
- Verify `NEXT_PUBLIC_API_URL` in frontend .env

## Important Disclaimers

- This application is for **educational and research purposes only**
- Past performance does not guarantee future results
- This is **not investment advice** or a recommendation to buy or sell securities
- Factor returns shown are based on academic research and may not reflect actual investable returns
- All data is sourced from publicly available AQR research datasets
- Users must respect AQR's terms of use for their data

## License

This project is provided as-is for educational purposes. All AQR data remains subject to AQR Capital Management's terms and conditions.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues, questions, or suggestions:

1. Check the troubleshooting section above
2. Review existing GitHub issues
3. Open a new issue with detailed information

## Acknowledgments

- **AQR Capital Management** for providing publicly available factor research data
- **FastAPI** and **Next.js** communities for excellent documentation and tools
- Academic researchers whose work on factor investing made this possible

---

Built with ❤️ for the quantitative finance community
