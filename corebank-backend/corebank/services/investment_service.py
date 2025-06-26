"""
Investment service for CoreBank.

This module provides business logic for investment and wealth management operations.
"""

import logging
from datetime import datetime, timedelta, timezone, date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID

from corebank.models.investment import (
    ProductType, RiskLevel, TransactionType, TransactionStatus, HoldingStatus,
    InvestmentProductCreate, InvestmentProductUpdate, InvestmentProductResponse,
    RiskAssessmentCreate, RiskAssessmentResponse,
    InvestmentPurchaseRequest, InvestmentRedemptionRequest,
    InvestmentTransactionResponse, InvestmentHoldingResponse,
    PortfolioSummaryResponse, ProductNAVResponse, ProductRecommendationResponse
)
from corebank.repositories.postgres_repo import PostgresRepository
from corebank.core.exceptions import (
    ValidationError, NotFoundError, InsufficientFundsError, BusinessRuleError
)

logger = logging.getLogger(__name__)


class InvestmentService:
    """Service for investment operations."""
    
    def __init__(self, repository: PostgresRepository):
        """Initialize investment service."""
        self.repository = repository
    
    # Product Management
    async def get_products(
        self,
        product_type: Optional[ProductType] = None,
        risk_level: Optional[RiskLevel] = None,
        is_active: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[InvestmentProductResponse]:
        """Get investment products with filtering."""
        try:
            filters = {"is_active": is_active}
            if product_type:
                filters["product_type"] = product_type.value
            if risk_level:
                filters["risk_level"] = risk_level.value
            
            products = await self.repository.get_investment_products(
                filters=filters, skip=skip, limit=limit
            )
            
            return [InvestmentProductResponse.model_validate(product) for product in products]
            
        except Exception as e:
            logger.error(f"Failed to get investment products: {e}")
            raise
    
    async def get_product(self, product_id: UUID) -> InvestmentProductResponse:
        """Get a specific investment product."""
        try:
            product = await self.repository.get_investment_product(product_id)
            if not product:
                raise NotFoundError(f"Investment product {product_id} not found")
            
            return InvestmentProductResponse.model_validate(product)
            
        except Exception as e:
            logger.error(f"Failed to get investment product {product_id}: {e}")
            raise
    
    async def create_product(self, product_data: InvestmentProductCreate) -> InvestmentProductResponse:
        """Create a new investment product."""
        try:
            # Check if product code already exists
            existing = await self.repository.get_investment_product_by_code(product_data.product_code)
            if existing:
                raise ValidationError(f"Product code {product_data.product_code} already exists")
            
            product = await self.repository.create_investment_product(product_data.model_dump())
            return InvestmentProductResponse.model_validate(product)
            
        except Exception as e:
            logger.error(f"Failed to create investment product: {e}")
            raise
    
    # Risk Assessment
    async def create_risk_assessment(
        self, 
        user_id: UUID, 
        assessment_data: RiskAssessmentCreate
    ) -> RiskAssessmentResponse:
        """Create or update user risk assessment."""
        try:
            # Calculate assessment score based on responses
            score = self._calculate_risk_score(assessment_data)
            
            # Set expiration date (1 year from now)
            expires_at = datetime.now(timezone.utc) + timedelta(days=365)
            
            assessment_dict = assessment_data.model_dump()
            assessment_dict.update({
                "user_id": user_id,
                "assessment_score": score,
                "expires_at": expires_at
            })
            
            assessment = await self.repository.create_risk_assessment(assessment_dict)
            return RiskAssessmentResponse.model_validate(assessment)
            
        except Exception as e:
            logger.error(f"Failed to create risk assessment for user {user_id}: {e}")
            raise
    
    async def get_user_risk_assessment(self, user_id: UUID) -> Optional[RiskAssessmentResponse]:
        """Get user's current valid risk assessment."""
        try:
            assessment = await self.repository.get_current_risk_assessment(user_id)
            if not assessment:
                return None

            # Check if assessment is still valid
            if assessment['expires_at'] < datetime.now(timezone.utc):
                return None

            return RiskAssessmentResponse.model_validate(assessment)

        except Exception as e:
            logger.error(f"Failed to get risk assessment for user {user_id}: {e}")
            raise
    
    # Investment Transactions
    async def purchase_investment(
        self, 
        user_id: UUID, 
        purchase_request: InvestmentPurchaseRequest
    ) -> InvestmentTransactionResponse:
        """Purchase an investment product."""
        try:
            async with await self.repository.transaction():
                # Validate product
                product = await self.repository.get_investment_product(purchase_request.product_id)
                if not product or not product.get('is_active'):
                    raise NotFoundError("Investment product not found or inactive")

                # Validate account ownership
                account = await self.repository.get_account_by_id(purchase_request.account_id)
                if not account or account.get('user_id') != user_id:
                    raise NotFoundError("Account not found or not owned by user")

                # Check minimum investment amount
                if purchase_request.amount < product.get('min_investment_amount'):
                    raise ValidationError(
                        f"Investment amount must be at least {product.get('min_investment_amount')}"
                    )

                # Check maximum investment amount
                max_amount = product.get('max_investment_amount')
                if max_amount and purchase_request.amount > max_amount:
                    raise ValidationError(
                        f"Investment amount cannot exceed {max_amount}"
                    )

                # Check account balance
                if account.get('balance') < purchase_request.amount:
                    raise InsufficientFundsError("Insufficient account balance")
                
                # Get current unit price (simplified - in real system would come from market data)
                unit_price = await self._get_current_unit_price(purchase_request.product_id)
                
                # Calculate shares and fees
                fee = self._calculate_purchase_fee(purchase_request.amount, ProductType(product.get('product_type')))
                net_amount = purchase_request.amount - fee
                shares = net_amount / unit_price

                # Deduct from account
                await self.repository.update_account_balance(
                    purchase_request.account_id,
                    account.get('balance') - purchase_request.amount
                )
                
                # Create or update holding
                holding = await self._create_or_update_holding(
                    user_id=user_id,
                    account_id=purchase_request.account_id,
                    product_id=purchase_request.product_id,
                    shares=shares,
                    unit_price=unit_price,
                    amount=net_amount,
                    product=product
                )
                
                # Create transaction record
                transaction_data = {
                    "user_id": user_id,
                    "account_id": purchase_request.account_id,
                    "product_id": purchase_request.product_id,
                    "holding_id": holding.get('id'),
                    "transaction_type": TransactionType.PURCHASE.value,
                    "shares": shares,
                    "unit_price": unit_price,
                    "amount": purchase_request.amount,
                    "fee": fee,
                    "net_amount": net_amount,
                    "status": TransactionStatus.CONFIRMED.value,
                    "settlement_date": datetime.now(timezone.utc),
                    "description": f"Purchase {product.get('name')}"
                }
                
                transaction = await self.repository.create_investment_transaction(transaction_data)
                return InvestmentTransactionResponse.model_validate(transaction)
                
        except Exception as e:
            logger.error(f"Failed to purchase investment for user {user_id}: {e}")
            raise
    
    async def redeem_investment(
        self, 
        user_id: UUID, 
        redemption_request: InvestmentRedemptionRequest
    ) -> InvestmentTransactionResponse:
        """Redeem an investment holding."""
        try:
            async with await self.repository.transaction():
                # Get holding
                holding = await self.repository.get_investment_holding(redemption_request.holding_id)
                if not holding or holding.get('user_id') != user_id:
                    raise NotFoundError("Investment holding not found or not owned by user")

                if holding.get('status') != HoldingStatus.ACTIVE.value:
                    raise BusinessRuleError("Cannot redeem inactive holding")

                # Determine shares to redeem
                shares_to_redeem = redemption_request.shares or holding.get('shares')
                if shares_to_redeem > holding.get('shares'):
                    raise ValidationError("Cannot redeem more shares than held")

                # Get current unit price
                unit_price = await self._get_current_unit_price(holding.get('product_id'))

                # Calculate redemption amount and fees
                gross_amount = shares_to_redeem * unit_price
                fee = self._calculate_redemption_fee(gross_amount, ProductType(holding.get('product_type')))
                net_amount = gross_amount - fee

                # Update holding
                remaining_shares = holding.get('shares') - shares_to_redeem
                if remaining_shares == 0:
                    # Full redemption
                    await self.repository.update_investment_holding_status(
                        redemption_request.holding_id, 
                        HoldingStatus.REDEEMED.value
                    )
                else:
                    # Partial redemption
                    await self.repository.update_investment_holding_shares(
                        redemption_request.holding_id, 
                        remaining_shares
                    )
                
                # Add to account balance
                account = await self.repository.get_account_by_id(holding.get('account_id'))
                await self.repository.update_account_balance(
                    holding.get('account_id'),
                    account.get('balance') + net_amount
                )
                
                # Create transaction record
                transaction_data = {
                    "user_id": user_id,
                    "account_id": holding.get('account_id'),
                    "product_id": holding.get('product_id'),
                    "holding_id": holding.get('id'),
                    "transaction_type": TransactionType.REDEMPTION.value,
                    "shares": shares_to_redeem,
                    "unit_price": unit_price,
                    "amount": gross_amount,
                    "fee": fee,
                    "net_amount": net_amount,
                    "status": TransactionStatus.CONFIRMED.value,
                    "settlement_date": datetime.now(timezone.utc),
                    "description": f"Redeem {holding.get('product_name')}"
                }
                
                transaction = await self.repository.create_investment_transaction(transaction_data)
                return InvestmentTransactionResponse.model_validate(transaction)
                
        except Exception as e:
            logger.error(f"Failed to redeem investment for user {user_id}: {e}")
            raise

    async def get_user_investment_transactions(
        self,
        user_id: UUID,
        product_id: Optional[UUID] = None,
        transaction_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[InvestmentTransactionResponse]:
        """Get user's investment transactions."""
        try:
            transactions = await self.repository.get_user_investment_transactions(
                user_id=user_id,
                product_id=product_id,
                transaction_type=transaction_type,
                skip=skip,
                limit=limit
            )

            return [InvestmentTransactionResponse.model_validate(transaction) for transaction in transactions]

        except Exception as e:
            logger.error(f"Failed to get investment transactions for user {user_id}: {e}")
            raise

    # Portfolio Management
    async def get_user_holdings(self, user_id: UUID) -> List[InvestmentHoldingResponse]:
        """Get user's investment holdings."""
        try:
            holdings = await self.repository.get_user_investment_holdings(user_id)
            
            # Calculate current values and returns
            enriched_holdings = []
            for holding in holdings:
                current_price = await self._get_current_unit_price(holding.get('product_id'))
                current_value = (holding.get('shares') * current_price).quantize(Decimal('0.0001'))
                unrealized_gain_loss = (current_value - holding.get('total_invested')).quantize(Decimal('0.0001'))

                # Calculate return rate with proper precision
                total_invested = holding.get('total_invested')
                if total_invested > 0:
                    return_rate = (unrealized_gain_loss / total_invested * 100).quantize(Decimal('0.0001'))
                else:
                    return_rate = Decimal('0.0000')

                holding_dict = holding.copy()
                holding_dict.update({
                    "current_value": current_value,
                    "unrealized_gain_loss": unrealized_gain_loss,
                    "return_rate": return_rate
                })

                enriched_holdings.append(InvestmentHoldingResponse(**holding_dict))
            
            return enriched_holdings
            
        except Exception as e:
            logger.error(f"Failed to get holdings for user {user_id}: {e}")
            raise
    
    async def get_portfolio_summary(self, user_id: UUID) -> PortfolioSummaryResponse:
        """Get user's portfolio summary."""
        try:
            all_holdings = await self.get_user_holdings(user_id)

            # Only include active holdings in portfolio calculations
            active_holdings = [h for h in all_holdings if h.status == HoldingStatus.ACTIVE]

            total_assets = sum(holding.current_value for holding in active_holdings)
            total_invested = sum(holding.total_invested for holding in active_holdings)
            total_gain_loss = total_assets - total_invested
            total_return_rate = (total_gain_loss / total_invested * 100) if total_invested > 0 else Decimal('0')

            # Calculate asset allocation (only for active holdings)
            asset_allocation = {}
            for holding in active_holdings:
                product_type = holding.product_type
                if product_type not in asset_allocation:
                    asset_allocation[product_type] = Decimal('0')
                asset_allocation[product_type] += holding.current_value

            # Convert to percentages
            if total_assets > 0:
                asset_allocation = {
                    k: (v / total_assets * 100) for k, v in asset_allocation.items()
                }

            return PortfolioSummaryResponse(
                total_assets=total_assets,
                total_invested=total_invested,
                total_gain_loss=total_gain_loss,
                total_return_rate=total_return_rate,
                asset_allocation=asset_allocation,
                holdings_count=len(all_holdings),
                active_products_count=len(active_holdings)
            )
            
        except Exception as e:
            logger.error(f"Failed to get portfolio summary for user {user_id}: {e}")
            raise
    
    # Helper methods
    def _calculate_risk_score(self, assessment: RiskAssessmentCreate) -> int:
        """Calculate risk assessment score."""
        score = 0
        
        # Risk tolerance (40% weight)
        score += assessment.risk_tolerance.value * 8
        
        # Investment experience (30% weight)
        experience_scores = {"beginner": 1, "intermediate": 3, "advanced": 5}
        score += experience_scores[assessment.investment_experience.value] * 6
        
        # Investment goal (20% weight)
        goal_scores = {"wealth_preservation": 1, "steady_growth": 3, "aggressive_growth": 5}
        score += goal_scores[assessment.investment_goal.value] * 4
        
        # Investment horizon (10% weight)
        horizon_scores = {"short_term": 1, "medium_term": 3, "long_term": 5}
        score += horizon_scores[assessment.investment_horizon.value] * 2
        
        return min(score, 100)  # Cap at 100
    
    async def _get_current_unit_price(self, product_id: UUID) -> Decimal:
        """Get current unit price for a product."""
        # Simplified implementation - in real system would fetch from market data
        latest_nav = await self.repository.get_latest_product_nav(product_id)
        if latest_nav:
            return Decimal(str(latest_nav['unit_nav']))
        return Decimal('1.0000')  # Default for new products
    
    def _calculate_purchase_fee(self, amount: Decimal, product_type: ProductType) -> Decimal:
        """Calculate purchase fee based on product type."""
        fee_rates = {
            ProductType.MONEY_FUND: Decimal('0.0000'),  # No fee
            ProductType.FIXED_TERM: Decimal('0.0050'),  # 0.5%
            ProductType.MUTUAL_FUND: Decimal('0.0150'), # 1.5%
            ProductType.INSURANCE: Decimal('0.0200'),   # 2.0%
        }
        return amount * fee_rates.get(product_type, Decimal('0.0100'))
    
    def _calculate_redemption_fee(self, amount: Decimal, product_type: ProductType) -> Decimal:
        """Calculate redemption fee based on product type."""
        fee_rates = {
            ProductType.MONEY_FUND: Decimal('0.0000'),  # No fee
            ProductType.FIXED_TERM: Decimal('0.0025'),  # 0.25%
            ProductType.MUTUAL_FUND: Decimal('0.0075'), # 0.75%
            ProductType.INSURANCE: Decimal('0.0100'),   # 1.0%
        }
        return amount * fee_rates.get(product_type, Decimal('0.0050'))
    
    async def _create_or_update_holding(
        self,
        user_id: UUID,
        account_id: UUID,
        product_id: UUID,
        shares: Decimal,
        unit_price: Decimal,
        amount: Decimal,
        product: dict = None
    ):
        """Create new holding or update existing one."""
        # Check for existing active holding
        existing = await self.repository.get_user_product_holding(user_id, product_id)
        
        if existing and existing.get('status') == HoldingStatus.ACTIVE.value:
            # Update existing holding
            new_shares = existing.get('shares') + shares
            new_total_invested = existing.get('total_invested') + amount
            new_average_cost = new_total_invested / new_shares

            await self.repository.update_investment_holding(
                existing.get('id'),
                {
                    "shares": new_shares,
                    "average_cost": new_average_cost,
                    "total_invested": new_total_invested,
                    "updated_at": datetime.now(timezone.utc)
                }
            )
            return existing
        else:
            # Create new holding
            # Calculate maturity date for fixed-term products
            maturity_date = None
            if product and product.get('product_type') == ProductType.FIXED_TERM.value and product.get('investment_period_days'):
                maturity_date = datetime.now(timezone.utc) + timedelta(days=int(product.get('investment_period_days')))

            holding_data = {
                "user_id": user_id,
                "account_id": account_id,
                "product_id": product_id,
                "shares": shares,
                "average_cost": unit_price,
                "total_invested": amount,
                "current_value": amount,
                "purchase_date": datetime.now(timezone.utc),
                "maturity_date": maturity_date,
                "status": HoldingStatus.ACTIVE.value
            }
            
            return await self.repository.create_investment_holding(holding_data)

    async def get_product_recommendations(self, user_id: UUID) -> List[ProductRecommendationResponse]:
        """
        Get personalized product recommendations based on user's risk assessment.

        Args:
            user_id: User ID

        Returns:
            List[ProductRecommendationResponse]: List of recommended products
        """
        try:
            # Get user's risk assessment
            risk_assessment = await self.repository.get_user_risk_assessment(user_id)
            if not risk_assessment:
                # No risk assessment, return conservative recommendations
                return await self._get_default_recommendations()

            # Get all active products
            products = await self.repository.get_investment_products(
                filters={"is_active": True},
                skip=0,
                limit=100
            )

            # Filter and score products based on risk assessment
            recommendations = []
            user_risk_level = RiskLevel(risk_assessment.risk_tolerance)

            for product in products:
                product_risk_level = RiskLevel(product.risk_level)

                # Calculate recommendation score
                score = self._calculate_recommendation_score(
                    user_risk_level,
                    product_risk_level,
                    risk_assessment
                )

                # Only recommend products with score > 0.3
                if score > 0.3:
                    recommendation = ProductRecommendationResponse(
                        product=InvestmentProductResponse.model_validate(product),
                        recommendation_score=score,
                        recommendation_reason=self._get_recommendation_reason(
                            user_risk_level,
                            product_risk_level,
                            product
                        ),
                        risk_match=abs(user_risk_level.value - product_risk_level.value) <= 1,
                        suggested_allocation=self._get_suggested_allocation(
                            user_risk_level,
                            product_risk_level
                        )
                    )
                    recommendations.append(recommendation)

            # Sort by recommendation score (highest first) and limit to top 5
            recommendations.sort(key=lambda x: x.recommendation_score, reverse=True)
            return recommendations[:5]

        except Exception as e:
            logger.error(f"Failed to get product recommendations for user {user_id}: {e}")
            # Return default recommendations on error
            return await self._get_default_recommendations()

    def _calculate_recommendation_score(
        self,
        user_risk_level: RiskLevel,
        product_risk_level: RiskLevel,
        risk_assessment
    ) -> float:
        """Calculate recommendation score for a product."""
        base_score = 1.0

        # Risk level matching (40% weight)
        risk_diff = abs(user_risk_level.value - product_risk_level.value)
        if risk_diff == 0:
            risk_score = 1.0
        elif risk_diff == 1:
            risk_score = 0.8
        elif risk_diff == 2:
            risk_score = 0.5
        else:
            risk_score = 0.2

        # Investment experience factor (30% weight)
        experience_factor = {
            "beginner": 0.7 if product_risk_level.value <= 2 else 0.3,
            "intermediate": 0.9 if product_risk_level.value <= 3 else 0.6,
            "advanced": 1.0
        }.get(risk_assessment.investment_experience, 0.7)

        # Investment goal alignment (30% weight)
        goal_factor = {
            "wealth_preservation": 1.0 if product_risk_level.value <= 2 else 0.4,
            "steady_growth": 1.0 if product_risk_level.value <= 3 else 0.6,
            "aggressive_growth": 1.0 if product_risk_level.value >= 3 else 0.5
        }.get(risk_assessment.investment_goal, 0.7)

        final_score = base_score * (0.4 * risk_score + 0.3 * experience_factor + 0.3 * goal_factor)
        return min(final_score, 1.0)

    def _get_recommendation_reason(
        self,
        user_risk_level: RiskLevel,
        product_risk_level: RiskLevel,
        product
    ) -> str:
        """Generate recommendation reason."""
        if user_risk_level == product_risk_level:
            return f"该产品的风险等级与您的风险承受能力完全匹配，适合您的投资需求。"
        elif abs(user_risk_level.value - product_risk_level.value) == 1:
            if product_risk_level.value < user_risk_level.value:
                return f"该产品风险较低，可以作为稳健配置的一部分，平衡您的投资组合。"
            else:
                return f"该产品收益潜力较高，可以适当配置以提升整体收益。"
        else:
            return f"该产品具有良好的历史表现，建议少量配置以分散风险。"

    def _get_suggested_allocation(
        self,
        user_risk_level: RiskLevel,
        product_risk_level: RiskLevel
    ) -> Optional[Decimal]:
        """Get suggested allocation percentage."""
        risk_diff = abs(user_risk_level.value - product_risk_level.value)

        if risk_diff == 0:
            # Perfect match
            return Decimal('30.0')  # 30%
        elif risk_diff == 1:
            # Close match
            return Decimal('20.0')  # 20%
        elif risk_diff == 2:
            # Moderate match
            return Decimal('10.0')  # 10%
        else:
            # Low match
            return Decimal('5.0')   # 5%

    async def _get_default_recommendations(self) -> List[ProductRecommendationResponse]:
        """Get default conservative recommendations for users without risk assessment."""
        try:
            # Get low-risk products
            products = await self.repository.get_investment_products(
                filters={"is_active": True, "risk_level": RiskLevel.LOW.value},
                skip=0,
                limit=3
            )

            recommendations = []
            for i, product in enumerate(products):
                score = 0.8 - (i * 0.1)  # Decreasing scores
                recommendation = ProductRecommendationResponse(
                    product=InvestmentProductResponse.model_validate(product),
                    recommendation_score=score,
                    recommendation_reason="推荐给未完成风险评估的用户的稳健型产品。",
                    risk_match=True,
                    suggested_allocation=Decimal('20.0')
                )
                recommendations.append(recommendation)

            return recommendations

        except Exception as e:
            logger.error(f"Failed to get default recommendations: {e}")
            return []
