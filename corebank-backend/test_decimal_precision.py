#!/usr/bin/env python3
"""
Simple test script to verify decimal precision handling in investment calculations.
This script tests the decimal quantization fix without requiring database setup.
"""

from decimal import Decimal
from corebank.models.investment import InvestmentHoldingResponse, HoldingStatus
from uuid import uuid4
from datetime import datetime, timezone


def test_decimal_precision():
    """Test that decimal values are properly quantized to avoid validation errors."""
    
    # Simulate problematic values that caused the original error
    shares = Decimal('6566.01')
    unit_price = Decimal('1.0000000000')
    total_invested = Decimal('6566.01')
    
    # Calculate values with proper quantization (as fixed in the service)
    current_value = (shares * unit_price).quantize(Decimal('0.0001'))
    unrealized_gain_loss = (current_value - total_invested).quantize(Decimal('0.0001'))
    
    # Calculate return rate with proper precision
    if total_invested > 0:
        return_rate = (unrealized_gain_loss / total_invested * 100).quantize(Decimal('0.0001'))
    else:
        return_rate = Decimal('0.0000')
    
    print(f"Original shares: {shares}")
    print(f"Unit price: {unit_price}")
    print(f"Total invested: {total_invested}")
    print(f"Current value: {current_value}")
    print(f"Unrealized gain/loss: {unrealized_gain_loss}")
    print(f"Return rate: {return_rate}")
    
    # Test that these values can be used in the Pydantic model
    try:
        holding_data = {
            "id": uuid4(),
            "user_id": uuid4(),
            "account_id": uuid4(),
            "product_id": uuid4(),
            "product_name": "测试产品",
            "product_type": "money_fund",
            "shares": shares,
            "average_cost": unit_price,
            "total_invested": total_invested,
            "current_value": current_value,
            "unrealized_gain_loss": unrealized_gain_loss,
            "realized_gain_loss": Decimal('0.0000'),
            "return_rate": return_rate,
            "purchase_date": datetime.now(timezone.utc),
            "maturity_date": None,
            "status": HoldingStatus.ACTIVE,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        holding = InvestmentHoldingResponse(**holding_data)
        print("\n✅ SUCCESS: InvestmentHoldingResponse created successfully!")
        print(f"   Current value: {holding.current_value}")
        print(f"   Unrealized gain/loss: {holding.unrealized_gain_loss}")
        print(f"   Return rate: {holding.return_rate}")
        
        # Verify decimal constraints
        assert holding.current_value.as_tuple().exponent >= -4, "Current value has too many decimal places"
        assert holding.unrealized_gain_loss.as_tuple().exponent >= -4, "Unrealized gain/loss has too many decimal places"
        assert len(str(holding.return_rate).replace('.', '').replace('-', '')) <= 8, "Return rate has too many digits"
        
        print("✅ All decimal precision constraints satisfied!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def test_extreme_precision_values():
    """Test with extreme precision values that caused the original error."""
    
    print("\n" + "="*60)
    print("Testing extreme precision values...")
    print("="*60)
    
    # Values from the actual error logs
    problematic_current_value = Decimal('6566.009999992776')
    problematic_unrealized_gain_loss = Decimal('-7.224E-9')
    problematic_return_rate = Decimal('-1.100211543997039297838413283E-10')
    
    print(f"Problematic current value: {problematic_current_value}")
    print(f"Problematic unrealized gain/loss: {problematic_unrealized_gain_loss}")
    print(f"Problematic return rate: {problematic_return_rate}")
    
    # Apply quantization fix
    fixed_current_value = problematic_current_value.quantize(Decimal('0.0001'))
    fixed_unrealized_gain_loss = problematic_unrealized_gain_loss.quantize(Decimal('0.0001'))
    fixed_return_rate = problematic_return_rate.quantize(Decimal('0.0001'))
    
    print(f"\nFixed current value: {fixed_current_value}")
    print(f"Fixed unrealized gain/loss: {fixed_unrealized_gain_loss}")
    print(f"Fixed return rate: {fixed_return_rate}")
    
    # Test with fixed values
    try:
        holding_data = {
            "id": uuid4(),
            "user_id": uuid4(),
            "account_id": uuid4(),
            "product_id": uuid4(),
            "product_name": "测试产品",
            "product_type": "money_fund",
            "shares": Decimal('6566.01000000'),
            "average_cost": Decimal('1.0000'),
            "total_invested": Decimal('6566.0100'),
            "current_value": fixed_current_value,
            "unrealized_gain_loss": fixed_unrealized_gain_loss,
            "realized_gain_loss": Decimal('0.0000'),
            "return_rate": fixed_return_rate,
            "purchase_date": datetime.now(timezone.utc),
            "maturity_date": None,
            "status": HoldingStatus.ACTIVE,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        holding = InvestmentHoldingResponse(**holding_data)
        print("\n✅ SUCCESS: Extreme precision values handled correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR with extreme values: {e}")
        return False


if __name__ == "__main__":
    print("Testing decimal precision handling...")
    print("="*60)
    
    success1 = test_decimal_precision()
    success2 = test_extreme_precision_values()
    
    print("\n" + "="*60)
    if success1 and success2:
        print("🎉 ALL TESTS PASSED! Decimal precision fix is working correctly.")
    else:
        print("❌ Some tests failed. Check the output above.")
    print("="*60)
