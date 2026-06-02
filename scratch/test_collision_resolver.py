import sqlite3
import os

def resolve_ma_hang(tk_id, db_path='raw_archive.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get the Ma_Hang from database for this tk_id
    cursor.execute("SELECT Ma_Hang FROM listings WHERE tk_id = ?", (tk_id,))
    row = cursor.fetchone()
    ma_hang_db = row[0] if row else ""
    
    if not ma_hang_db:
        # Fallback to last part of tk_id
        parts = tk_id.split('-')
        suffix = parts[-1].upper() if parts else ""
        conn.close()
        return f"TK-{suffix}"
        
    # Check if there is a collision in SQLite for this Ma_Hang
    cursor.execute("SELECT COUNT(DISTINCT tk_id) FROM listings WHERE Ma_Hang = ?", (ma_hang_db,))
    count = cursor.fetchone()[0]
    
    if count > 1:
        # Collision detected! Resolve by using the last part of tk_id (usually 8 hex chars)
        parts = tk_id.split('-')
        suffix = parts[-1].upper() if parts else ""
        resolved = f"TK-{suffix}"
        print(f"[COLLISION RESOLVED] tk_id: {tk_id} had Ma_Hang: {ma_hang_db} (collides with {count-1} other listings). Resolved to: {resolved}")
        conn.close()
        return resolved
    else:
        conn.close()
        return ma_hang_db

# Test with the two colliding listings
print("Testing resolving colliding listings:")
print(resolve_ma_hang('fedjlr-mna1q7ua-3d5e5437'))
print(resolve_ma_hang('cv5xsr-mhyaft63-485e5437'))

# Test with a normal listing
print("\nTesting resolving a normal listing:")
print(resolve_ma_hang('excs3z-m36z9qk1-ffcb1'))
