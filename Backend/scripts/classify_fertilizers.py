#!/usr/bin/env python3
"""
Script to classify fertilizers as organic (Hữu cơ) or inorganic (Vô cơ)
based on their name and composition.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from database import SessionLocal
from models.input import PhanBon


def classify_fertilizer(name: str, composition: str = '') -> str:
    """
    Classify fertilizer as organic or inorganic based on keywords.
    
    Args:
        name: Fertilizer name
        composition: Fertilizer composition/ingredients
        
    Returns:
        'Hữu cơ' for organic, 'Vô cơ' for inorganic
    """
    text = (name + ' ' + (composition or '')).lower()
    
    # Keywords indicating organic fertilizers
    organic_keywords = [
        'hữu cơ',
        'vi sinh',
        'phân chuồng',
        'compost',
        'sinh học',
        'organic',
        'bio',
        'hữu co',  # typo variation
        'phân bón vi sinh',
        'phân hữu cơ'
    ]
    
    # Check for organic keywords
    for keyword in organic_keywords:
        if keyword in text:
            return 'Hữu cơ'
    
    # Default to inorganic
    return 'Vô cơ'


def main():
    """Main function to classify all fertilizers in the database."""
    db = SessionLocal()
    
    try:
        # Get all fertilizers
        fertilizers = db.query(PhanBon).all()
        total = len(fertilizers)
        
        print(f"Found {total} fertilizers to classify...")
        
        # Classify each fertilizer
        updated = 0
        organic_count = 0
        inorganic_count = 0
        
        for fert in fertilizers:
            # Only update if not already classified
            if not fert.loai_phan_bon:
                classification = classify_fertilizer(
                    fert.ten_phan_bon or '', 
                    fert.thanh_phan or ''
                )
                fert.loai_phan_bon = classification
                updated += 1
                
                if classification == 'Hữu cơ':
                    organic_count += 1
                else:
                    inorganic_count += 1
        
        # Commit changes
        db.commit()
        
        print(f"\n✅ Classification Complete!")
        print(f"   Total fertilizers: {total}")
        print(f"   Updated: {updated}")
        print(f"   Hữu cơ (Organic): {organic_count}")
        print(f"   Vô cơ (Inorganic): {inorganic_count}")
        
        # Show some examples
        print(f"\n📊 Sample Classifications:")
        samples = db.query(PhanBon).limit(10).all()
        for s in samples:
            print(f"   - {s.ten_phan_bon[:50]}: {s.loai_phan_bon}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
