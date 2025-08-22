from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text
from datetime import date, datetime, timedelta
from decimal import Decimal
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import logging

from .models import Vendor, Invoice, Payment, VendorPerformanceMetrics, APAnalytics
from .schemas import (
    FraudDetectionResponse, DuplicateDetectionResponse, 
    SmartCategorizationResponse, CashFlowForecastResponse
)

logger = logging.getLogger(__name__)

class APAIService:
    """AI/ML service for Accounts Payable module"""
    
    def __init__(self, db: Session):
        self.db = db
        self.fraud_model = None
        self.categorization_model = None
        self.cash_flow_model = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ML models"""
        try:
            # Initialize fraud detection model
            self.fraud_model = IsolationForest(
                contamination=0.1,
                random_state=42,
                n_estimators=100
            )
            
            # Initialize categorization model
            self.categorization_model = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                max_depth=10
            )
            
            # Train models with existing data
            self._train_models()
            
        except Exception as e:
            logger.error(f"Error initializing AI models: {str(e)}")
    
    def _train_models(self):
        """Train ML models with historical data"""
        try:
            # Train fraud detection model
            fraud_features = self._extract_fraud_features()
            if len(fraud_features) > 10:
                self.fraud_model.fit(fraud_features)
            
            # Train categorization model
            cat_features, cat_labels = self._extract_categorization_features()
            if len(cat_features) > 10:
                self.categorization_model.fit(cat_features, cat_labels)
                
        except Exception as e:
            logger.error(f"Error training models: {str(e)}")
    
    def _extract_fraud_features(self) -> np.ndarray:
        """Extract features for fraud detection"""
        try:
            # Get invoice data for fraud detection
            invoices = self.db.query(Invoice).filter(
                Invoice.created_at >= datetime.now() - timedelta(days=365)
            ).all()
            
            features = []
            for invoice in invoices:
                feature_vector = [
                    float(invoice.total_amount),
                    (invoice.due_date - invoice.invoice_date).days,
                    len(invoice.lines),
                    float(invoice.total_amount / len(invoice.lines)) if invoice.lines else 0,
                    1 if invoice.received_date else 0,
                    invoice.vendor.risk_level.value == 'high',
                    (datetime.now().date() - invoice.invoice_date).days,
                ]
                features.append(feature_vector)
            
            return np.array(features) if features else np.array([]).reshape(0, 7)
            
        except Exception as e:
            logger.error(f"Error extracting fraud features: {str(e)}")
            return np.array([]).reshape(0, 7)
    
    def _extract_categorization_features(self) -> Tuple[np.ndarray, np.ndarray]:
        """Extract features for expense categorization"""
        try:
            # Get invoice line data
            query = text("""
                SELECT il.description, il.category, il.unit_price, il.quantity,
                       v.category as vendor_category, il.line_total
                FROM ap_invoice_lines il
                JOIN ap_invoices i ON il.invoice_id = i.id
                JOIN ap_vendors v ON i.vendor_id = v.id
                WHERE il.category IS NOT NULL
                AND il.created_at >= :date_limit
            """)
            
            result = self.db.execute(query, {
                'date_limit': datetime.now() - timedelta(days=365)
            }).fetchall()
            
            features = []
            labels = []
            
            for row in result:
                # Simple feature extraction (in production, use more sophisticated NLP)
                desc_length = len(row.description) if row.description else 0
                feature_vector = [
                    desc_length,
                    float(row.unit_price) if row.unit_price else 0,
                    float(row.quantity) if row.quantity else 0,
                    float(row.line_total) if row.line_total else 0,
                    hash(row.vendor_category.value) % 1000 if row.vendor_category else 0,
                ]
                features.append(feature_vector)
                labels.append(row.category)
            
            return np.array(features), np.array(labels)
            
        except Exception as e:
            logger.error(f"Error extracting categorization features: {str(e)}")
            return np.array([]).reshape(0, 5), np.array([])
    
    def detect_fraud(self, invoice_id: int) -> FraudDetectionResponse:
        """Detect potential fraud in invoice"""
        try:
            invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
            if not invoice:
                raise ValueError(f"Invoice {invoice_id} not found")
            
            # Extract features for this invoice
            feature_vector = np.array([[
                float(invoice.total_amount),
                (invoice.due_date - invoice.invoice_date).days,
                len(invoice.lines),
                float(invoice.total_amount / len(invoice.lines)) if invoice.lines else 0,
                1 if invoice.received_date else 0,
                invoice.vendor.risk_level.value == 'high',
                (datetime.now().date() - invoice.invoice_date).days,
            ]])
            
            # Predict fraud score
            if self.fraud_model and hasattr(self.fraud_model, 'decision_function'):
                fraud_score = self.fraud_model.decision_function(feature_vector)[0]
                # Normalize to 0-100 scale
                fraud_score = max(0, min(100, (fraud_score + 1) * 50))
            else:
                fraud_score = 0
            
            # Determine risk level
            if fraud_score > 80:
                risk_level = "critical"
            elif fraud_score > 60:
                risk_level = "high"
            elif fraud_score > 40:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            # Generate risk factors
            risk_factors = []
            if invoice.total_amount > 10000:
                risk_factors.append("High invoice amount")
            if invoice.vendor.risk_level.value in ['high', 'critical']:
                risk_factors.append("High-risk vendor")
            if (invoice.due_date - invoice.invoice_date).days < 7:
                risk_factors.append("Unusually short payment terms")
            if not invoice.received_date:
                risk_factors.append("No receipt date recorded")
            
            # Generate recommendations
            recommendations = []
            if fraud_score > 60:
                recommendations.append("Require additional approval")
                recommendations.append("Verify invoice with vendor")
            if fraud_score > 40:
                recommendations.append("Review supporting documents")
            
            # Update invoice with fraud score
            invoice.fraud_risk_score = Decimal(str(fraud_score))
            self.db.commit()
            
            return FraudDetectionResponse(
                invoice_id=invoice_id,
                fraud_risk_score=Decimal(str(fraud_score)),
                risk_level=risk_level,
                risk_factors=risk_factors,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error in fraud detection: {str(e)}")
            return FraudDetectionResponse(
                invoice_id=invoice_id,
                fraud_risk_score=Decimal('0'),
                risk_level="low",
                risk_factors=[],
                recommendations=[]
            )
    
    def detect_duplicates(self, invoice_id: int) -> DuplicateDetectionResponse:
        """Detect potential duplicate invoices"""
        try:
            invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
            if not invoice:
                raise ValueError(f"Invoice {invoice_id} not found")
            
            # Find potential duplicates based on multiple criteria
            potential_duplicates = []
            
            # Check for exact invoice number match
            exact_matches = self.db.query(Invoice).filter(
                and_(
                    Invoice.id != invoice_id,
                    Invoice.vendor_id == invoice.vendor_id,
                    Invoice.invoice_number == invoice.invoice_number
                )
            ).all()
            
            for match in exact_matches:
                potential_duplicates.append({
                    "invoice_id": match.id,
                    "invoice_number": match.invoice_number,
                    "match_type": "exact_number",
                    "confidence": 95,
                    "amount": float(match.total_amount),
                    "date": match.invoice_date.isoformat()
                })
            
            # Check for similar amount and date
            date_range = timedelta(days=7)
            amount_tolerance = invoice.total_amount * Decimal('0.05')  # 5% tolerance
            
            similar_matches = self.db.query(Invoice).filter(
                and_(
                    Invoice.id != invoice_id,
                    Invoice.vendor_id == invoice.vendor_id,
                    Invoice.invoice_date >= invoice.invoice_date - date_range,
                    Invoice.invoice_date <= invoice.invoice_date + date_range,
                    Invoice.total_amount >= invoice.total_amount - amount_tolerance,
                    Invoice.total_amount <= invoice.total_amount + amount_tolerance
                )
            ).all()
            
            for match in similar_matches:
                if match.id not in [d["invoice_id"] for d in potential_duplicates]:
                    confidence = 70
                    if abs(match.total_amount - invoice.total_amount) < amount_tolerance * Decimal('0.1'):
                        confidence += 15
                    if abs((match.invoice_date - invoice.invoice_date).days) <= 1:
                        confidence += 10
                    
                    potential_duplicates.append({
                        "invoice_id": match.id,
                        "invoice_number": match.invoice_number,
                        "match_type": "similar_amount_date",
                        "confidence": confidence,
                        "amount": float(match.total_amount),
                        "date": match.invoice_date.isoformat()
                    })
            
            # Calculate overall confidence
            if potential_duplicates:
                confidence_score = max([d["confidence"] for d in potential_duplicates])
            else:
                confidence_score = 0
            
            # Determine matching criteria
            matching_criteria = []
            if any(d["match_type"] == "exact_number" for d in potential_duplicates):
                matching_criteria.append("Exact invoice number match")
            if any(d["match_type"] == "similar_amount_date" for d in potential_duplicates):
                matching_criteria.append("Similar amount and date")
            
            # Update invoice with duplicate risk score
            invoice.duplicate_risk_score = Decimal(str(confidence_score))
            self.db.commit()
            
            return DuplicateDetectionResponse(
                invoice_id=invoice_id,
                potential_duplicates=potential_duplicates,
                confidence_score=Decimal(str(confidence_score)),
                matching_criteria=matching_criteria
            )
            
        except Exception as e:
            logger.error(f"Error in duplicate detection: {str(e)}")
            return DuplicateDetectionResponse(
                invoice_id=invoice_id,
                potential_duplicates=[],
                confidence_score=Decimal('0'),
                matching_criteria=[]
            )
    
    def smart_categorization(self, line_item_id: int) -> SmartCategorizationResponse:
        """Predict category for invoice line item"""
        try:
            # Get line item
            query = text("""
                SELECT il.*, i.vendor_id, v.category as vendor_category
                FROM ap_invoice_lines il
                JOIN ap_invoices i ON il.invoice_id = i.id
                JOIN ap_vendors v ON i.vendor_id = v.id
                WHERE il.id = :line_id
            """)
            
            result = self.db.execute(query, {'line_id': line_item_id}).fetchone()
            if not result:
                raise ValueError(f"Line item {line_item_id} not found")
            
            # Extract features
            desc_length = len(result.description) if result.description else 0
            feature_vector = np.array([[
                desc_length,
                float(result.unit_price) if result.unit_price else 0,
                float(result.quantity) if result.quantity else 0,
                float(result.line_total) if result.line_total else 0,
                hash(result.vendor_category.value) % 1000 if result.vendor_category else 0,
            ]])
            
            # Predict category
            if (self.categorization_model and 
                hasattr(self.categorization_model, 'predict_proba') and
                len(self.categorization_model.classes_) > 0):
                
                probabilities = self.categorization_model.predict_proba(feature_vector)[0]
                predicted_idx = np.argmax(probabilities)
                predicted_category = self.categorization_model.classes_[predicted_idx]
                confidence = probabilities[predicted_idx] * 100
                
                # Get alternative categories
                sorted_indices = np.argsort(probabilities)[::-1]
                alternatives = []
                for i in sorted_indices[1:4]:  # Top 3 alternatives
                    if probabilities[i] > 0.1:  # Only if probability > 10%
                        alternatives.append({
                            "category": self.categorization_model.classes_[i],
                            "confidence": probabilities[i] * 100
                        })
            else:
                # Fallback to rule-based categorization
                predicted_category = self._rule_based_categorization(result.description, result.vendor_category)
                confidence = 60
                alternatives = []
            
            return SmartCategorizationResponse(
                line_item_id=line_item_id,
                predicted_category=predicted_category,
                confidence_score=Decimal(str(confidence)),
                suggested_account=None,  # Could be enhanced with GL account mapping
                alternative_categories=alternatives
            )
            
        except Exception as e:
            logger.error(f"Error in smart categorization: {str(e)}")
            return SmartCategorizationResponse(
                line_item_id=line_item_id,
                predicted_category="Other",
                confidence_score=Decimal('0'),
                alternative_categories=[]
            )
    
    def _rule_based_categorization(self, description: str, vendor_category) -> str:
        """Fallback rule-based categorization"""
        if not description:
            return "Other"
        
        desc_lower = description.lower()
        
        # Office supplies
        if any(word in desc_lower for word in ['paper', 'pen', 'office', 'supplies', 'stationery']):
            return "Office Supplies"
        
        # Travel
        if any(word in desc_lower for word in ['travel', 'hotel', 'flight', 'taxi', 'uber']):
            return "Travel & Entertainment"
        
        # Utilities
        if any(word in desc_lower for word in ['electric', 'gas', 'water', 'internet', 'phone']):
            return "Utilities"
        
        # Professional services
        if any(word in desc_lower for word in ['consulting', 'legal', 'audit', 'professional']):
            return "Professional Services"
        
        # Based on vendor category
        if vendor_category:
            if vendor_category.value == 'utility':
                return "Utilities"
            elif vendor_category.value == 'consultant':
                return "Professional Services"
            elif vendor_category.value == 'supplier':
                return "Materials & Supplies"
        
        return "Other"
    
    def predict_cash_flow(self, days_ahead: int = 30) -> CashFlowForecastResponse:
        """Predict cash flow for AP payments"""
        try:
            forecast_date = date.today() + timedelta(days=days_ahead)
            
            # Get pending invoices
            pending_invoices = self.db.query(Invoice).filter(
                and_(
                    Invoice.status.in_(['approved', 'pending_approval']),
                    Invoice.balance_due > 0,
                    Invoice.due_date <= forecast_date
                )
            ).all()
            
            predicted_payments = []
            total_amount = Decimal('0')
            
            for invoice in pending_invoices:
                # Calculate payment probability based on various factors
                days_until_due = (invoice.due_date - date.today()).days
                vendor_reliability = invoice.vendor.reliability_score or Decimal('75')
                
                # Payment probability calculation
                if days_until_due <= 0:  # Overdue
                    probability = 0.9
                elif days_until_due <= 7:  # Due within a week
                    probability = 0.8
                elif days_until_due <= 30:  # Due within a month
                    probability = 0.7
                else:
                    probability = 0.5
                
                # Adjust based on vendor reliability
                probability *= float(vendor_reliability) / 100
                
                predicted_amount = invoice.balance_due * Decimal(str(probability))
                
                predicted_payments.append({
                    "invoice_id": invoice.id,
                    "invoice_number": invoice.invoice_number,
                    "vendor_name": invoice.vendor.name,
                    "due_date": invoice.due_date.isoformat(),
                    "amount": float(invoice.balance_due),
                    "predicted_amount": float(predicted_amount),
                    "probability": probability,
                    "days_until_due": days_until_due
                })
                
                total_amount += predicted_amount
            
            # Calculate confidence score
            if predicted_payments:
                avg_probability = sum(p["probability"] for p in predicted_payments) / len(predicted_payments)
                confidence_score = Decimal(str(avg_probability * 100))
            else:
                confidence_score = Decimal('100')
            
            # Identify risk factors
            risk_factors = []
            overdue_count = sum(1 for p in predicted_payments if p["days_until_due"] < 0)
            if overdue_count > 0:
                risk_factors.append(f"{overdue_count} overdue invoices")
            
            high_amount_count = sum(1 for p in predicted_payments if p["amount"] > 10000)
            if high_amount_count > 0:
                risk_factors.append(f"{high_amount_count} high-value payments")
            
            return CashFlowForecastResponse(
                forecast_date=forecast_date,
                period_days=days_ahead,
                predicted_payments=predicted_payments,
                total_predicted_amount=total_amount,
                confidence_score=confidence_score,
                risk_factors=risk_factors
            )
            
        except Exception as e:
            logger.error(f"Error in cash flow prediction: {str(e)}")
            return CashFlowForecastResponse(
                forecast_date=date.today(),
                period_days=days_ahead,
                predicted_payments=[],
                total_predicted_amount=Decimal('0'),
                confidence_score=Decimal('0'),
                risk_factors=["Error in prediction model"]
            )
    
    def calculate_vendor_risk_score(self, vendor_id: int) -> Decimal:
        """Calculate AI-based risk score for vendor"""
        try:
            vendor = self.db.query(Vendor).filter(Vendor.id == vendor_id).first()
            if not vendor:
                return Decimal('50')  # Default medium risk
            
            risk_score = Decimal('0')
            
            # Payment history analysis
            recent_invoices = self.db.query(Invoice).filter(
                and_(
                    Invoice.vendor_id == vendor_id,
                    Invoice.created_at >= datetime.now() - timedelta(days=365)
                )
            ).all()
            
            if recent_invoices:
                # Calculate average payment delay
                paid_invoices = [inv for inv in recent_invoices if inv.status == 'paid']
                if paid_invoices:
                    # This would need payment date tracking for accurate calculation
                    avg_delay = 0  # Placeholder
                    if avg_delay > 30:
                        risk_score += Decimal('20')
                    elif avg_delay > 15:
                        risk_score += Decimal('10')
                
                # Dispute rate
                disputed_count = sum(1 for inv in recent_invoices if inv.status == 'disputed')
                dispute_rate = disputed_count / len(recent_invoices)
                risk_score += Decimal(str(dispute_rate * 30))
                
                # Invoice amount volatility
                amounts = [float(inv.total_amount) for inv in recent_invoices]
                if len(amounts) > 1:
                    volatility = np.std(amounts) / np.mean(amounts)
                    risk_score += Decimal(str(min(volatility * 20, 20)))
            
            # Vendor characteristics
            if vendor.risk_level == 'high':
                risk_score += Decimal('25')
            elif vendor.risk_level == 'medium':
                risk_score += Decimal('15')
            
            # Compliance score impact
            compliance_impact = (100 - vendor.compliance_score) / 4
            risk_score += Decimal(str(compliance_impact))
            
            # Cap at 100
            risk_score = min(risk_score, Decimal('100'))
            
            # Update vendor AI risk score
            vendor.ai_risk_score = risk_score
            self.db.commit()
            
            return risk_score
            
        except Exception as e:
            logger.error(f"Error calculating vendor risk score: {str(e)}")
            return Decimal('50')
    
    def generate_payment_recommendations(self, vendor_id: int) -> List[Dict[str, Any]]:
        """Generate AI-powered payment recommendations"""
        try:
            vendor = self.db.query(Vendor).filter(Vendor.id == vendor_id).first()
            if not vendor:
                return []
            
            recommendations = []
            
            # Get pending invoices
            pending_invoices = self.db.query(Invoice).filter(
                and_(
                    Invoice.vendor_id == vendor_id,
                    Invoice.status == 'approved',
                    Invoice.balance_due > 0
                )
            ).all()
            
            if not pending_invoices:
                return recommendations
            
            # Early payment discount opportunities
            for invoice in pending_invoices:
                days_until_due = (invoice.due_date - date.today()).days
                if days_until_due > 10 and vendor.discount_percentage > 0:
                    discount_amount = invoice.balance_due * vendor.discount_percentage / 100
                    recommendations.append({
                        "type": "early_payment_discount",
                        "invoice_id": invoice.id,
                        "invoice_number": invoice.invoice_number,
                        "message": f"Pay early to save {discount_amount:.2f} ({vendor.discount_percentage}% discount)",
                        "priority": "medium",
                        "potential_savings": float(discount_amount)
                    })
            
            # Overdue payment alerts
            overdue_invoices = [inv for inv in pending_invoices if inv.due_date < date.today()]
            if overdue_invoices:
                total_overdue = sum(inv.balance_due for inv in overdue_invoices)
                recommendations.append({
                    "type": "overdue_alert",
                    "message": f"{len(overdue_invoices)} overdue invoices totaling {total_overdue:.2f}",
                    "priority": "high",
                    "invoice_count": len(overdue_invoices),
                    "total_amount": float(total_overdue)
                })
            
            # Batch payment opportunities
            if len(pending_invoices) > 3:
                total_amount = sum(inv.balance_due for inv in pending_invoices)
                recommendations.append({
                    "type": "batch_payment",
                    "message": f"Consider batch payment for {len(pending_invoices)} invoices ({total_amount:.2f})",
                    "priority": "low",
                    "invoice_count": len(pending_invoices),
                    "total_amount": float(total_amount)
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating payment recommendations: {str(e)}")
            return []