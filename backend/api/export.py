"""
Data export API routes: CSV, Excel exports
"""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import pandas as pd
import io

from backend.db import get_db
from backend.models import Factor, FactorReturn

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/factor/{factor_id}/csv")
def export_factor_csv(
    factor_id: int,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Export factor time series as CSV"""
    # Get factor
    factor = db.query(Factor).filter(Factor.id == factor_id).first()
    if not factor:
        raise HTTPException(status_code=404, detail="Factor not found")

    # Get returns
    query = db.query(FactorReturn).filter(FactorReturn.factor_id == factor_id)
    if start_date:
        query = query.filter(FactorReturn.date >= start_date)
    if end_date:
        query = query.filter(FactorReturn.date <= end_date)

    returns = query.order_by(FactorReturn.date).all()

    if not returns:
        raise HTTPException(status_code=404, detail="No data found")

    # Create DataFrame
    df = pd.DataFrame([
        {"date": r.date, "return": r.return_value}
        for r in returns
    ])

    # Convert to CSV
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    stream.seek(0)

    filename = f"{factor.code}_returns.csv"

    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/factor/{factor_id}/excel")
def export_factor_excel(
    factor_id: int,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Export factor time series as Excel"""
    # Get factor
    factor = db.query(Factor).filter(Factor.id == factor_id).first()
    if not factor:
        raise HTTPException(status_code=404, detail="Factor not found")

    # Get returns
    query = db.query(FactorReturn).filter(FactorReturn.factor_id == factor_id)
    if start_date:
        query = query.filter(FactorReturn.date >= start_date)
    if end_date:
        query = query.filter(FactorReturn.date <= end_date)

    returns = query.order_by(FactorReturn.date).all()

    if not returns:
        raise HTTPException(status_code=404, detail="No data found")

    # Create DataFrame
    df = pd.DataFrame([
        {
            "Date": r.date,
            "Return": r.return_value,
            "Cumulative Return": None  # Will calculate
        }
        for r in returns
    ])

    # Calculate cumulative returns
    df['Cumulative Return'] = (1 + df['Return']).cumprod() - 1

    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Write data sheet
        df.to_excel(writer, sheet_name='Returns', index=False)

        # Write metadata sheet
        metadata_df = pd.DataFrame([
            {"Property": "Factor Code", "Value": factor.code},
            {"Property": "Factor Name", "Value": factor.name},
            {"Property": "Region", "Value": factor.region},
            {"Property": "Frequency", "Value": factor.frequency},
            {"Property": "First Date", "Value": str(factor.first_date)},
            {"Property": "Last Date", "Value": str(factor.last_date)},
            {"Property": "Annualized Return", "Value": factor.annualized_return},
            {"Property": "Volatility", "Value": factor.annualized_volatility},
            {"Property": "Sharpe Ratio", "Value": factor.sharpe_ratio},
            {"Property": "Max Drawdown", "Value": factor.max_drawdown},
        ])
        metadata_df.to_excel(writer, sheet_name='Metadata', index=False)

    output.seek(0)

    filename = f"{factor.code}_analysis.xlsx"

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/factors/summary/csv")
def export_all_factors_summary_csv(
    region: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Export summary of all factors as CSV"""
    query = db.query(Factor)

    if region:
        query = query.filter(Factor.region == region)

    factors = query.all()

    if not factors:
        raise HTTPException(status_code=404, detail="No factors found")

    # Create DataFrame
    df = pd.DataFrame([
        {
            "Code": f.code,
            "Name": f.name,
            "Region": f.region,
            "Asset Class": f.asset_class,
            "Frequency": f.frequency,
            "First Date": f.first_date,
            "Last Date": f.last_date,
            "Annualized Return": f.annualized_return,
            "Volatility": f.annualized_volatility,
            "Sharpe Ratio": f.sharpe_ratio,
            "Max Drawdown": f.max_drawdown,
        }
        for f in factors
    ])

    # Convert to CSV
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    stream.seek(0)

    filename = f"factors_summary_{region if region else 'all'}.csv"

    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
