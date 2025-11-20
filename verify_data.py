from backend.db import SessionLocal
from backend.models import Factor, FactorReturn

def verify():
    db = SessionLocal()
    try:
        factors = db.query(Factor).count()
        returns = db.query(FactorReturn).count()
        print(f"Factors: {factors}")
        print(f"Returns: {returns}")
        
        if factors > 0 and returns > 0:
            print("VERIFICATION SUCCESS: Data found in database.")
        else:
            print("VERIFICATION FAILURE: No data found.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify()
