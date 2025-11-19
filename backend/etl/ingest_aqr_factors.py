"""
ETL module to ingest AQR factor CSV files into the database

This module handles:
- Reading AQR factor CSV files from a local directory
- Parsing and normalizing the data
- Computing basic statistics
- Upserting data into the PostgreSQL database

Usage:
    python -m backend.etl.ingest_aqr_factors --data-dir ./data/aqr_raw
"""

import argparse
import os
import sys
import logging
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import select

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.models import Factor, FactorReturn, FactorGroup
from backend.db import SessionLocal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Factor metadata mapping for known AQR datasets
# This maps file patterns to factor metadata
FACTOR_METADATA = {
    'qmj': {
        'name': 'Quality Minus Junk',
        'group': 'Quality',
        'asset_class': 'Equity',
        'description': 'Long high-quality stocks and short low-quality (junk) stocks'
    },
    'bab': {
        'name': 'Betting Against Beta',
        'group': 'Low Risk',
        'asset_class': 'Equity',
        'description': 'Long low-beta stocks and short high-beta stocks'
    },
    'hml_devil': {
        'name': 'HML Devil',
        'group': 'Value',
        'asset_class': 'Equity',
        'description': 'Value factor with improvements addressing the "Devil in HML\'s Details"'
    },
    'hmld': {
        'name': 'HML Devil',
        'group': 'Value',
        'asset_class': 'Equity',
        'description': 'Value factor with improvements addressing the "Devil in HML\'s Details"'
    },
    'mom': {
        'name': 'Momentum',
        'group': 'Momentum',
        'asset_class': 'Equity',
        'description': 'Long past winners and short past losers'
    },
    'umd': {
        'name': 'Up Minus Down (Momentum)',
        'group': 'Momentum',
        'asset_class': 'Equity',
        'description': 'Momentum factor: long past winners, short past losers'
    },
    'tsmom': {
        'name': 'Time Series Momentum',
        'group': 'Momentum',
        'asset_class': 'Multi-Asset',
        'description': 'Trend-following strategy across multiple asset classes'
    },
    'vme': {
        'name': 'Value and Momentum Everywhere',
        'group': 'Multi-Factor',
        'asset_class': 'Multi-Asset',
        'description': 'Combined value and momentum across stocks, bonds, commodities, and currencies'
    },
    'smb': {
        'name': 'Small Minus Big',
        'group': 'Size',
        'asset_class': 'Equity',
        'description': 'Size premium: long small-cap stocks, short large-cap stocks'
    },
    'mkt': {
        'name': 'Market Factor',
        'group': 'Market',
        'asset_class': 'Equity',
        'description': 'Market excess return (market return minus risk-free rate)'
    },
}

REGION_MAPPING = {
    'usa': 'US',
    'us': 'US',
    'global': 'Global',
    'glb': 'Global',
    'intl': 'International',
    'europe': 'Europe',
    'eur': 'Europe',
    'japan': 'Japan',
    'jpn': 'Japan',
    'asia_pacific': 'Asia Pacific',
    'apac': 'Asia Pacific',
    'emerging': 'Emerging Markets',
    'em': 'Emerging Markets',
    'dev_ex_us': 'Developed ex US',
}


def parse_aqr_csv(file_path: Path) -> Tuple[pd.DataFrame, Dict]:
    """
    Parse an AQR CSV file and extract returns data and metadata

    Returns:
        Tuple of (DataFrame with date and return columns, metadata dict)
    """
    logger.info(f"Parsing file: {file_path.name}")

    # Read the CSV file - AQR files typically have metadata rows at the top
    # We'll read the file in chunks to identify the header row
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Find the header row (usually contains 'DATE' or 'date')
    header_row = 0
    for i, line in enumerate(lines[:20]):  # Check first 20 lines
        if 'DATE' in line.upper() or 'Date' in line:
            header_row = i
            break

    # Read the CSV starting from the header row
    df = pd.read_csv(file_path, skiprows=header_row)

    # Extract metadata from filename
    filename = file_path.stem.lower()
    metadata = extract_metadata_from_filename(filename)

    # Clean up the dataframe
    df = clean_aqr_dataframe(df)

    return df, metadata


def extract_metadata_from_filename(filename: str) -> Dict:
    """
    Extract factor metadata from filename

    AQR files typically follow patterns like:
    - QMJ_Factors_Monthly.csv
    - BAB_US_daily.csv
    - HML_Devil_Global.csv
    """
    metadata = {
        'provider': 'AQR',
        'frequency': 'Monthly',  # Default
        'region': 'US',  # Default
        'asset_class': 'Equity',  # Default
        'group': 'Other',
        'name': filename.upper(),
        'description': ''
    }

    filename_lower = filename.lower()

    # Detect frequency
    if 'daily' in filename_lower:
        metadata['frequency'] = 'Daily'
    elif 'monthly' in filename_lower:
        metadata['frequency'] = 'Monthly'

    # Detect region
    for key, value in REGION_MAPPING.items():
        if key in filename_lower:
            metadata['region'] = value
            break

    # Detect factor type from filename and apply metadata
    for factor_key, factor_info in FACTOR_METADATA.items():
        if factor_key in filename_lower:
            metadata.update(factor_info)
            break

    return metadata


def clean_aqr_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and normalize an AQR dataframe

    - Standardize date column
    - Convert returns to decimal format
    - Remove any non-data rows
    """
    # Identify date column (case insensitive)
    date_col = None
    for col in df.columns:
        if col.upper() in ['DATE', 'DATES', 'YEAR', 'MONTH']:
            date_col = col
            break

    if date_col is None:
        raise ValueError("Could not find date column in CSV")

    # Rename to standard 'date'
    df = df.rename(columns={date_col: 'date'})

    # Parse dates
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Remove rows with invalid dates
    df = df.dropna(subset=['date'])

    # Get return columns (everything except date)
    return_cols = [col for col in df.columns if col != 'date']

    # Convert return columns to numeric
    for col in return_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Sort by date
    df = df.sort_values('date')

    # Remove duplicates
    df = df.drop_duplicates(subset=['date'])

    return df


def compute_factor_statistics(returns: pd.Series, frequency: str = 'Monthly') -> Dict:
    """
    Compute summary statistics for a factor's returns

    Args:
        returns: Series of returns (in decimal format)
        frequency: 'Daily' or 'Monthly'

    Returns:
        Dictionary of statistics
    """
    if len(returns) == 0 or returns.isna().all():
        return {
            'total_return': None,
            'annualized_return': None,
            'annualized_volatility': None,
            'max_drawdown': None,
            'sharpe_ratio': None
        }

    # Remove NaN values
    returns_clean = returns.dropna()

    if len(returns_clean) == 0:
        return {
            'total_return': None,
            'annualized_return': None,
            'annualized_volatility': None,
            'max_drawdown': None,
            'sharpe_ratio': None
        }

    # Periods per year
    periods_per_year = 252 if frequency == 'Daily' else 12

    # Total return (cumulative)
    total_return = (1 + returns_clean).prod() - 1

    # Annualized return
    n_periods = len(returns_clean)
    years = n_periods / periods_per_year
    annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0

    # Annualized volatility
    annualized_volatility = returns_clean.std() * np.sqrt(periods_per_year)

    # Sharpe ratio (assuming 0 risk-free rate for simplicity)
    sharpe_ratio = annualized_return / annualized_volatility if annualized_volatility > 0 else 0

    # Max drawdown
    cumulative = (1 + returns_clean).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = drawdown.min()

    return {
        'total_return': float(total_return),
        'annualized_return': float(annualized_return),
        'annualized_volatility': float(annualized_volatility),
        'max_drawdown': float(max_drawdown),
        'sharpe_ratio': float(sharpe_ratio)
    }


def get_or_create_factor_group(db: Session, group_name: str) -> FactorGroup:
    """Get or create a factor group"""
    group_code = group_name.lower().replace(' ', '_')

    group = db.query(FactorGroup).filter(FactorGroup.code == group_code).first()

    if not group:
        group = FactorGroup(
            code=group_code,
            name=group_name,
            description=f"{group_name} factors"
        )
        db.add(group)
        db.commit()
        db.refresh(group)
        logger.info(f"Created factor group: {group_name}")

    return group


def ingest_factor_file(db: Session, file_path: Path) -> int:
    """
    Ingest a single AQR factor file

    Returns:
        Number of factors ingested from this file
    """
    try:
        # Parse the CSV file
        df, base_metadata = parse_aqr_csv(file_path)

        if df.empty:
            logger.warning(f"No data found in {file_path.name}")
            return 0

        # Get return columns (all columns except 'date')
        return_columns = [col for col in df.columns if col != 'date']

        factors_ingested = 0

        for return_col in return_columns:
            # Create factor code from filename and column name
            factor_code = f"{file_path.stem}_{return_col}".lower()
            factor_code = factor_code.replace(' ', '_').replace('-', '_')

            # Prepare factor metadata
            metadata = base_metadata.copy()

            # If the column name contains region info, update metadata
            col_lower = return_col.lower()
            for region_key, region_value in REGION_MAPPING.items():
                if region_key in col_lower:
                    metadata['region'] = region_value
                    break

            # Set factor name
            if return_col.strip() and return_col.upper() != return_col:
                metadata['name'] = f"{metadata['name']} - {return_col}"

            # Get or create factor group
            group = get_or_create_factor_group(db, metadata['group'])

            # Get returns for this column
            returns = df[['date', return_col]].copy()
            returns = returns.rename(columns={return_col: 'return_value'})
            returns = returns.dropna()

            if returns.empty:
                logger.warning(f"No valid returns for {factor_code}")
                continue

            # Compute statistics
            stats = compute_factor_statistics(
                returns['return_value'],
                metadata['frequency']
            )

            # Check if factor already exists
            factor = db.query(Factor).filter(Factor.code == factor_code).first()

            if factor:
                # Update existing factor
                logger.info(f"Updating existing factor: {factor_code}")
                factor.name = metadata['name']
                factor.region = metadata['region']
                factor.asset_class = metadata['asset_class']
                factor.frequency = metadata['frequency']
                factor.description = metadata['description']
                factor.group_id = group.id
                factor.first_date = returns['date'].min().date()
                factor.last_date = returns['date'].max().date()
                factor.total_return = stats['total_return']
                factor.annualized_return = stats['annualized_return']
                factor.annualized_volatility = stats['annualized_volatility']
                factor.max_drawdown = stats['max_drawdown']
                factor.sharpe_ratio = stats['sharpe_ratio']
                factor.updated_at = datetime.utcnow()
            else:
                # Create new factor
                logger.info(f"Creating new factor: {factor_code}")
                factor = Factor(
                    code=factor_code,
                    name=metadata['name'],
                    provider=metadata['provider'],
                    region=metadata['region'],
                    asset_class=metadata['asset_class'],
                    frequency=metadata['frequency'],
                    description=metadata['description'],
                    group_id=group.id,
                    first_date=returns['date'].min().date(),
                    last_date=returns['date'].max().date(),
                    total_return=stats['total_return'],
                    annualized_return=stats['annualized_return'],
                    annualized_volatility=stats['annualized_volatility'],
                    max_drawdown=stats['max_drawdown'],
                    sharpe_ratio=stats['sharpe_ratio']
                )
                db.add(factor)

            db.commit()
            db.refresh(factor)

            # Upsert returns data
            logger.info(f"Ingesting {len(returns)} return observations for {factor_code}")

            for _, row in returns.iterrows():
                return_date = row['date'].date()
                return_value = row['return_value']

                # Check if return already exists
                existing_return = db.query(FactorReturn).filter(
                    FactorReturn.factor_id == factor.id,
                    FactorReturn.date == return_date
                ).first()

                if existing_return:
                    # Update if value changed
                    if existing_return.return_value != return_value:
                        existing_return.return_value = return_value
                        existing_return.updated_at = datetime.utcnow()
                else:
                    # Insert new return
                    new_return = FactorReturn(
                        factor_id=factor.id,
                        date=return_date,
                        return_value=return_value
                    )
                    db.add(new_return)

            db.commit()

            logger.info(f"Successfully ingested factor: {factor_code}")
            logger.info(f"  Date range: {factor.first_date} to {factor.last_date}")
            logger.info(f"  Annualized return: {factor.annualized_return:.2%}" if factor.annualized_return else "  Annualized return: N/A")
            logger.info(f"  Volatility: {factor.annualized_volatility:.2%}" if factor.annualized_volatility else "  Volatility: N/A")
            logger.info(f"  Sharpe ratio: {factor.sharpe_ratio:.2f}" if factor.sharpe_ratio else "  Sharpe ratio: N/A")

            factors_ingested += 1

        return factors_ingested

    except Exception as e:
        logger.error(f"Error ingesting file {file_path.name}: {str(e)}")
        db.rollback()
        return 0


def ingest_directory(data_dir: str):
    """
    Ingest all CSV files from a directory

    Args:
        data_dir: Path to directory containing AQR CSV files
    """
    data_path = Path(data_dir)

    if not data_path.exists():
        logger.error(f"Directory does not exist: {data_dir}")
        return

    if not data_path.is_dir():
        logger.error(f"Not a directory: {data_dir}")
        return

    # Find all CSV files
    csv_files = list(data_path.glob("*.csv"))

    if not csv_files:
        logger.warning(f"No CSV files found in {data_dir}")
        return

    logger.info(f"Found {len(csv_files)} CSV files to process")

    db = SessionLocal()

    try:
        total_factors = 0

        for csv_file in csv_files:
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing file: {csv_file.name}")
            logger.info(f"{'='*60}")

            factors_count = ingest_factor_file(db, csv_file)
            total_factors += factors_count

        logger.info(f"\n{'='*60}")
        logger.info(f"Ingestion complete!")
        logger.info(f"Total factors ingested/updated: {total_factors}")
        logger.info(f"{'='*60}")

    finally:
        db.close()


def main():
    """Main entry point for ETL script"""
    parser = argparse.ArgumentParser(
        description="Ingest AQR factor CSV files into the database"
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        required=True,
        help='Directory containing AQR CSV files'
    )

    args = parser.parse_args()

    ingest_directory(args.data_dir)


if __name__ == "__main__":
    main()
