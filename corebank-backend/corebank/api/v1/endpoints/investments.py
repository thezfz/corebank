"""
Investment endpoints for CoreBank API.

This module provides REST API endpoints for investment and wealth management operations.
"""

import logging
from typing import List, Optional, Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer

from corebank.api.v1.dependencies import (
    get_current_user, get_investment_service
)
from corebank.models.investment import (
    ProductType, RiskLevel,
    InvestmentProductResponse, InvestmentProductCreate,
    RiskAssessmentCreate, RiskAssessmentResponse,
    InvestmentPurchaseRequest, InvestmentRedemptionRequest,
    InvestmentTransactionResponse, InvestmentHoldingResponse,
    PortfolioSummaryResponse, ProductRecommendationResponse
)
# from corebank.models.user import dict
from corebank.models.common import PaginatedResponse, MessageResponse
from corebank.services.investment_service import InvestmentService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/investments", tags=["Investments"])
security = HTTPBearer()


@router.get("/products", response_model=List[InvestmentProductResponse])
async def get_investment_products(
    product_type: Optional[ProductType] = Query(None, description="Filter by product type"),
    risk_level: Optional[RiskLevel] = Query(None, description="Filter by risk level"),
    is_active: bool = Query(True, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    investment_service: Annotated[InvestmentService, Depends(get_investment_service)] = None
) -> List[InvestmentProductResponse]:
    """
    Get investment products with optional filtering.
    
    Args:
        product_type: Filter by product type
        risk_level: Filter by risk level
        is_active: Filter by active status
        pagination: Pagination parameters
        investment_service: Investment service dependency
        
    Returns:
        List[InvestmentProductResponse]: List of investment products
    """
    try:
        products = await investment_service.get_products(
            product_type=product_type,
            risk_level=risk_level,
            is_active=is_active,
            skip=skip,
            limit=limit
        )
        
        logger.info(f"Retrieved {len(products)} investment products")
        return products
        
    except Exception as e:
        logger.error(f"Failed to get investment products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve investment products"
        )


@router.get("/products/{product_id}", response_model=InvestmentProductResponse)
async def get_investment_product(
    product_id: UUID,
    investment_service: Annotated[InvestmentService, Depends(get_investment_service)] = None
) -> InvestmentProductResponse:
    """
    Get a specific investment product.
    
    Args:
        product_id: Product unique identifier
        investment_service: Investment service dependency
        
    Returns:
        InvestmentProductResponse: Investment product details
    """
    try:
        product = await investment_service.get_product(product_id)
        logger.info(f"Retrieved investment product {product_id}")
        return product
        
    except Exception as e:
        logger.error(f"Failed to get investment product {product_id}: {e}")
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Investment product {product_id} not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve investment product"
        )


@router.post("/risk-assessment", response_model=RiskAssessmentResponse)
async def create_risk_assessment(
    assessment_data: RiskAssessmentCreate,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    investment_service: Annotated[InvestmentService, Depends(get_investment_service)] = None
) -> RiskAssessmentResponse:
    """
    Create or update user risk assessment.
    
    Args:
        assessment_data: Risk assessment data
        current_user: Current authenticated user
        investment_service: Investment service dependency
        
    Returns:
        RiskAssessmentResponse: Created risk assessment
    """
    try:
        assessment = await investment_service.create_risk_assessment(
            user_id=current_user['id'],
            assessment_data=assessment_data
        )
        
        logger.info(f"Created risk assessment for user {current_user['id']}")
        return assessment
        
    except Exception as e:
        logger.error(f"Failed to create risk assessment for user {current_user['id']}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create risk assessment"
        )


@router.get("/risk-assessment", response_model=Optional[RiskAssessmentResponse])
async def get_risk_assessment(
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    investment_service: Annotated[InvestmentService, Depends(get_investment_service)] = None
) -> Optional[RiskAssessmentResponse]:
    """
    Get user's current risk assessment.
    
    Args:
        current_user: Current authenticated user
        investment_service: Investment service dependency
        
    Returns:
        Optional[RiskAssessmentResponse]: Current risk assessment or None
    """
    try:
        assessment = await investment_service.get_user_risk_assessment(current_user['id'])
        logger.info(f"Retrieved risk assessment for user {current_user['id']}")
        return assessment
        
    except Exception as e:
        logger.error(f"Failed to get risk assessment for user {current_user['id']}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve risk assessment"
        )


@router.post("/purchase", response_model=InvestmentTransactionResponse)
async def purchase_investment(
    purchase_request: InvestmentPurchaseRequest,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    investment_service: Annotated[InvestmentService, Depends(get_investment_service)] = None
) -> InvestmentTransactionResponse:
    """
    Purchase an investment product.
    
    Args:
        purchase_request: Investment purchase request
        current_user: Current authenticated user
        investment_service: Investment service dependency
        
    Returns:
        InvestmentTransactionResponse: Purchase transaction details
    """
    try:
        transaction = await investment_service.purchase_investment(
            user_id=current_user['id'],
            purchase_request=purchase_request
        )
        
        logger.info(f"User {current_user['id']} purchased investment {purchase_request.product_id}")
        return transaction
        
    except Exception as e:
        logger.error(f"Failed to purchase investment for user {current_user['id']}: {e}")
        
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        elif "insufficient" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        elif "validation" in str(e).lower() or "minimum" in str(e).lower() or "maximum" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to purchase investment"
        )


@router.post("/redeem", response_model=InvestmentTransactionResponse)
async def redeem_investment(
    redemption_request: InvestmentRedemptionRequest,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    investment_service: Annotated[InvestmentService, Depends(get_investment_service)] = None
) -> InvestmentTransactionResponse:
    """
    Redeem an investment holding.
    
    Args:
        redemption_request: Investment redemption request
        current_user: Current authenticated user
        investment_service: Investment service dependency
        
    Returns:
        InvestmentTransactionResponse: Redemption transaction details
    """
    try:
        transaction = await investment_service.redeem_investment(
            user_id=current_user['id'],
            redemption_request=redemption_request
        )
        
        logger.info(f"User {current_user['id']} redeemed investment holding {redemption_request.holding_id}")
        return transaction
        
    except Exception as e:
        logger.error(f"Failed to redeem investment for user {current_user['id']}: {e}")
        
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        elif "cannot redeem" in str(e).lower() or "validation" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to redeem investment"
        )


@router.get("/holdings", response_model=List[InvestmentHoldingResponse])
async def get_investment_holdings(
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    investment_service: Annotated[InvestmentService, Depends(get_investment_service)] = None
) -> List[InvestmentHoldingResponse]:
    """
    Get user's investment holdings.
    
    Args:
        current_user: Current authenticated user
        investment_service: Investment service dependency
        
    Returns:
        List[InvestmentHoldingResponse]: List of investment holdings
    """
    try:
        holdings = await investment_service.get_user_holdings(current_user['id'])
        logger.info(f"Retrieved {len(holdings)} holdings for user {current_user['id']}")
        return holdings
        
    except Exception as e:
        logger.error(f"Failed to get holdings for user {current_user['id']}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve investment holdings"
        )


@router.get("/portfolio-summary", response_model=PortfolioSummaryResponse)
async def get_portfolio_summary(
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    investment_service: Annotated[InvestmentService, Depends(get_investment_service)] = None
) -> PortfolioSummaryResponse:
    """
    Get user's portfolio summary.
    
    Args:
        current_user: Current authenticated user
        investment_service: Investment service dependency
        
    Returns:
        PortfolioSummaryResponse: Portfolio summary
    """
    try:
        summary = await investment_service.get_portfolio_summary(current_user['id'])
        logger.info(f"Retrieved portfolio summary for user {current_user['id']}")
        return summary
        
    except Exception as e:
        logger.error(f"Failed to get portfolio summary for user {current_user['id']}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve portfolio summary"
        )


@router.get("/transactions", response_model=List[InvestmentTransactionResponse])
async def get_investment_transactions(
    product_id: Optional[UUID] = Query(None, description="Filter by product ID"),
    transaction_type: Optional[str] = Query(None, description="Filter by transaction type"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    investment_service: Annotated[InvestmentService, Depends(get_investment_service)] = None
) -> List[InvestmentTransactionResponse]:
    """
    Get user's investment transactions.

    Args:
        product_id: Filter by product ID
        transaction_type: Filter by transaction type
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Current authenticated user
        investment_service: Investment service dependency

    Returns:
        List[InvestmentTransactionResponse]: List of investment transactions
    """
    try:
        transactions = await investment_service.get_user_investment_transactions(
            user_id=current_user['id'],
            product_id=product_id,
            transaction_type=transaction_type,
            skip=skip,
            limit=limit
        )

        logger.info(f"Retrieved {len(transactions)} investment transactions for user {current_user['id']}")
        return transactions

    except Exception as e:
        logger.error(f"Failed to get investment transactions for user {current_user['id']}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve investment transactions"
        )


@router.get("/recommendations", response_model=List[ProductRecommendationResponse])
async def get_product_recommendations(
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    investment_service: Annotated[InvestmentService, Depends(get_investment_service)] = None
) -> List[ProductRecommendationResponse]:
    """
    Get personalized product recommendations.
    
    Args:
        current_user: Current authenticated user
        investment_service: Investment service dependency
        
    Returns:
        List[ProductRecommendationResponse]: List of recommended products
    """
    try:
        recommendations = await investment_service.get_product_recommendations(current_user['id'])
        logger.info(f"Retrieved {len(recommendations)} product recommendations for user {current_user['id']}")
        return recommendations

    except Exception as e:
        logger.error(f"Failed to get product recommendations for user {current_user['id']}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve product recommendations"
        )
