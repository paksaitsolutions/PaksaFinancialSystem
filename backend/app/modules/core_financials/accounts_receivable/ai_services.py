"""
AI/ML Services for Accounts Receivable
Predictive analytics, intelligent automation, and business intelligence
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import date, datetime, timedelta
from decimal import Decimal
import numpy as np
from dataclasses import dataclass
from enum import Enum
import json

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PaymentProbability(str, Enum):
    VERY_LOW = "very_low"    # 0-25%
    LOW = "low"              # 25-50%
    MEDIUM = "medium"        # 50-75%
    HIGH = "high"            # 75-90%
    VERY_HIGH = "very_high"  # 90-100%

@dataclass
class DelinquencyPrediction:
    customer_id: int
    invoice_id: Optional[int]
    risk_level: RiskLevel
    probability_score: float
    predicted_delay_days: int
    confidence_score: float
    risk_factors: List[str]
    recommendations: List[str]
    next_action_date: date

@dataclass
class PaymentForecast:
    invoice_id: int
    predicted_payment_date: date
    probability_range: PaymentProbability
    expected_amount: Decimal
    confidence_interval: Tuple[date, date]
    influencing_factors: List[str]

@dataclass
class CustomerSegment:
    segment_id: str
    segment_name: str
    characteristics: List[str]
    payment_behavior: str
    recommended_strategy: str
    automation_level: str

class ARPredictiveAnalytics:
    """Advanced AI/ML services for AR predictive analytics"""
    
    def __init__(self, db_session):
        self.db = db_session
        self.models_loaded = False
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained ML models (placeholder for actual model loading)"""
        # In production, load actual ML models (scikit-learn, TensorFlow, etc.)
        self.delinquency_model = None
        self.payment_timing_model = None
        self.customer_segmentation_model = None
        self.models_loaded = True
    
    def predict_delinquency(self, customer_id: int, invoice_id: Optional[int] = None) -> DelinquencyPrediction:
        """Predict likelihood of payment delinquency"""
        
        # Gather customer and invoice data
        customer_data = self._get_customer_features(customer_id)
        invoice_data = self._get_invoice_features(invoice_id) if invoice_id else {}
        
        # Feature engineering
        features = self._engineer_delinquency_features(customer_data, invoice_data)
        
        # ML prediction (simplified rule-based for demo)
        risk_score = self._calculate_risk_score(features)
        
        # Determine risk level
        if risk_score >= 0.8:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 0.6:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 0.4:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        # Generate insights
        risk_factors = self._identify_risk_factors(features)
        recommendations = self._generate_recommendations(risk_level, risk_factors)
        predicted_delay = self._predict_delay_days(risk_score)
        
        return DelinquencyPrediction(
            customer_id=customer_id,
            invoice_id=invoice_id,
            risk_level=risk_level,
            probability_score=risk_score,
            predicted_delay_days=predicted_delay,
            confidence_score=0.85,
            risk_factors=risk_factors,
            recommendations=recommendations,
            next_action_date=date.today() + timedelta(days=3)
        )
    
    def forecast_payment(self, invoice_id: int) -> PaymentForecast:
        """Forecast when an invoice will be paid"""
        
        invoice_data = self._get_invoice_features(invoice_id)
        customer_data = self._get_customer_features(invoice_data.get('customer_id'))
        
        # Predict payment timing
        base_days = customer_data.get('avg_payment_days', 30)
        risk_adjustment = self._calculate_timing_adjustment(customer_data, invoice_data)
        
        predicted_days = max(1, base_days + risk_adjustment)
        predicted_date = invoice_data.get('due_date', date.today()) + timedelta(days=predicted_days)
        
        # Determine probability range
        confidence = customer_data.get('payment_consistency', 0.7)
        if confidence >= 0.9:
            prob_range = PaymentProbability.VERY_HIGH
        elif confidence >= 0.75:
            prob_range = PaymentProbability.HIGH
        elif confidence >= 0.5:
            prob_range = PaymentProbability.MEDIUM
        elif confidence >= 0.25:
            prob_range = PaymentProbability.LOW
        else:
            prob_range = PaymentProbability.VERY_LOW
        
        # Confidence interval
        variance_days = max(3, int(predicted_days * 0.2))
        conf_start = predicted_date - timedelta(days=variance_days)
        conf_end = predicted_date + timedelta(days=variance_days)
        
        return PaymentForecast(
            invoice_id=invoice_id,
            predicted_payment_date=predicted_date,
            probability_range=prob_range,
            expected_amount=invoice_data.get('amount', Decimal('0')),
            confidence_interval=(conf_start, conf_end),
            influencing_factors=self._get_payment_factors(customer_data, invoice_data)
        )
    
    def segment_customers(self) -> List[CustomerSegment]:
        """AI-powered customer segmentation"""
        
        segments = [
            CustomerSegment(
                segment_id="champions",
                segment_name="Champions",
                characteristics=["High value", "Always pays on time", "Low maintenance"],
                payment_behavior="Excellent (0-5 days average)",
                recommended_strategy="Maintain relationship, offer incentives",
                automation_level="Minimal intervention"
            ),
            CustomerSegment(
                segment_id="loyal_customers",
                segment_name="Loyal Customers",
                characteristics=["Good value", "Usually pays on time", "Occasional delays"],
                payment_behavior="Good (5-15 days average)",
                recommended_strategy="Regular check-ins, payment reminders",
                automation_level="Standard automation"
            ),
            CustomerSegment(
                segment_id="potential_loyalists",
                segment_name="Potential Loyalists",
                characteristics=["Medium value", "Inconsistent payments", "Growth potential"],
                payment_behavior="Fair (15-30 days average)",
                recommended_strategy="Nurture relationship, flexible terms",
                automation_level="Enhanced monitoring"
            ),
            CustomerSegment(
                segment_id="at_risk",
                segment_name="At Risk",
                characteristics=["Declining payments", "Frequent disputes", "High maintenance"],
                payment_behavior="Poor (30+ days average)",
                recommended_strategy="Intensive management, credit review",
                automation_level="High intervention"
            ),
            CustomerSegment(
                segment_id="cannot_lose_them",
                segment_name="Cannot Lose Them",
                characteristics=["Very high value", "Strategic importance", "Occasional issues"],
                payment_behavior="Variable",
                recommended_strategy="White-glove service, dedicated support",
                automation_level="Manual oversight"
            )
        ]
        
        return segments
    
    def _get_customer_features(self, customer_id: int) -> Dict[str, Any]:
        """Extract customer features for ML models"""
        # In production, query actual database
        return {
            'customer_id': customer_id,
            'credit_score': 720,
            'payment_history_score': 0.85,
            'avg_payment_days': 25,
            'payment_consistency': 0.8,
            'total_outstanding': 15000,
            'credit_utilization': 0.6,
            'dispute_frequency': 0.1,
            'communication_responsiveness': 0.9,
            'industry_risk': 0.3,
            'company_size': 'medium',
            'geographic_risk': 0.2
        }
    
    def _get_invoice_features(self, invoice_id: int) -> Dict[str, Any]:
        """Extract invoice features for ML models"""
        return {
            'invoice_id': invoice_id,
            'amount': Decimal('5000'),
            'due_date': date.today() + timedelta(days=30),
            'invoice_age_days': 10,
            'payment_terms': 'net30',
            'has_disputes': False,
            'line_item_count': 3,
            'discount_applied': False,
            'seasonal_factor': 1.0,
            'customer_id': 1
        }
    
    def _engineer_delinquency_features(self, customer_data: Dict, invoice_data: Dict) -> Dict[str, float]:
        """Feature engineering for delinquency prediction"""
        features = {}
        
        # Customer-based features
        features['credit_score_norm'] = customer_data.get('credit_score', 600) / 850
        features['payment_history'] = customer_data.get('payment_history_score', 0.5)
        features['credit_utilization'] = customer_data.get('credit_utilization', 0.5)
        features['dispute_frequency'] = customer_data.get('dispute_frequency', 0.1)
        
        # Invoice-based features
        if invoice_data:
            features['invoice_amount_log'] = np.log(float(invoice_data.get('amount', 1000)))
            features['days_to_due'] = (invoice_data.get('due_date', date.today()) - date.today()).days
            features['has_disputes'] = 1.0 if invoice_data.get('has_disputes', False) else 0.0
        
        # Interaction features
        features['risk_interaction'] = features['credit_utilization'] * features['dispute_frequency']
        
        return features
    
    def _calculate_risk_score(self, features: Dict[str, float]) -> float:
        """Calculate overall risk score (simplified ML model)"""
        weights = {
            'credit_score_norm': -0.3,
            'payment_history': -0.4,
            'credit_utilization': 0.2,
            'dispute_frequency': 0.3,
            'invoice_amount_log': 0.1,
            'has_disputes': 0.2,
            'risk_interaction': 0.15
        }
        
        score = 0.5  # Base score
        for feature, weight in weights.items():
            if feature in features:
                score += features[feature] * weight
        
        return max(0.0, min(1.0, score))
    
    def _identify_risk_factors(self, features: Dict[str, float]) -> List[str]:
        """Identify key risk factors"""
        factors = []
        
        if features.get('credit_utilization', 0) > 0.8:
            factors.append("High credit utilization (>80%)")
        
        if features.get('payment_history', 1) < 0.7:
            factors.append("Poor payment history")
        
        if features.get('dispute_frequency', 0) > 0.2:
            factors.append("Frequent disputes")
        
        if features.get('has_disputes', 0) > 0:
            factors.append("Current invoice has disputes")
        
        if not factors:
            factors.append("Low risk profile")
        
        return factors
    
    def _generate_recommendations(self, risk_level: RiskLevel, risk_factors: List[str]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if risk_level == RiskLevel.CRITICAL:
            recommendations.extend([
                "Immediate contact required",
                "Consider credit hold",
                "Escalate to senior collections",
                "Review credit terms"
            ])
        elif risk_level == RiskLevel.HIGH:
            recommendations.extend([
                "Proactive outreach within 24 hours",
                "Offer payment plan options",
                "Monitor closely"
            ])
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.extend([
                "Send automated reminder",
                "Schedule follow-up in 3 days"
            ])
        else:
            recommendations.append("Standard monitoring")
        
        return recommendations
    
    def _predict_delay_days(self, risk_score: float) -> int:
        """Predict number of days payment will be delayed"""
        if risk_score >= 0.8:
            return 45
        elif risk_score >= 0.6:
            return 20
        elif risk_score >= 0.4:
            return 7
        else:
            return 0
    
    def _calculate_timing_adjustment(self, customer_data: Dict, invoice_data: Dict) -> int:
        """Calculate adjustment to base payment timing"""
        adjustment = 0
        
        # Customer factors
        if customer_data.get('payment_consistency', 1) < 0.7:
            adjustment += 10
        
        if customer_data.get('credit_utilization', 0) > 0.8:
            adjustment += 5
        
        # Invoice factors
        if invoice_data.get('amount', 0) > 10000:
            adjustment += 3
        
        if invoice_data.get('has_disputes', False):
            adjustment += 15
        
        return adjustment
    
    def _get_payment_factors(self, customer_data: Dict, invoice_data: Dict) -> List[str]:
        """Get factors influencing payment timing"""
        factors = []
        
        if customer_data.get('payment_consistency', 1) > 0.9:
            factors.append("Consistent payment history")
        
        if invoice_data.get('amount', 0) > 10000:
            factors.append("Large invoice amount")
        
        if customer_data.get('industry_risk', 0) > 0.5:
            factors.append("High-risk industry")
        
        factors.append("Seasonal payment patterns")
        factors.append("Customer payment terms")
        
        return factors

class ARIntelligentCollections:
    """Intelligent collections automation and optimization"""
    
    def __init__(self, db_session):
        self.db = db_session
        self.analytics = ARPredictiveAnalytics(db_session)
    
    def generate_collection_strategy(self, customer_id: int) -> Dict[str, Any]:
        """Generate personalized collection strategy"""
        
        prediction = self.analytics.predict_delinquency(customer_id)
        
        strategy = {
            'customer_id': customer_id,
            'risk_level': prediction.risk_level,
            'communication_channels': self._select_channels(customer_id, prediction.risk_level),
            'message_tone': self._select_tone(prediction.risk_level),
            'escalation_timeline': self._create_timeline(prediction.risk_level),
            'automation_level': self._determine_automation(prediction.risk_level),
            'next_actions': prediction.recommendations
        }
        
        return strategy
    
    def _select_channels(self, customer_id: int, risk_level: RiskLevel) -> List[str]:
        """Select optimal communication channels"""
        if risk_level == RiskLevel.CRITICAL:
            return ['phone', 'email', 'certified_mail']
        elif risk_level == RiskLevel.HIGH:
            return ['phone', 'email']
        else:
            return ['email', 'portal_notification']
    
    def _select_tone(self, risk_level: RiskLevel) -> str:
        """Select appropriate message tone"""
        tone_map = {
            RiskLevel.LOW: 'friendly_reminder',
            RiskLevel.MEDIUM: 'professional_reminder',
            RiskLevel.HIGH: 'urgent_notice',
            RiskLevel.CRITICAL: 'formal_demand'
        }
        return tone_map.get(risk_level, 'professional_reminder')
    
    def _create_timeline(self, risk_level: RiskLevel) -> List[Dict[str, Any]]:
        """Create escalation timeline"""
        if risk_level == RiskLevel.CRITICAL:
            return [
                {'day': 0, 'action': 'immediate_call', 'channel': 'phone'},
                {'day': 1, 'action': 'formal_notice', 'channel': 'email'},
                {'day': 3, 'action': 'escalate_manager', 'channel': 'phone'},
                {'day': 7, 'action': 'legal_notice', 'channel': 'certified_mail'}
            ]
        elif risk_level == RiskLevel.HIGH:
            return [
                {'day': 0, 'action': 'urgent_email', 'channel': 'email'},
                {'day': 2, 'action': 'follow_up_call', 'channel': 'phone'},
                {'day': 5, 'action': 'manager_review', 'channel': 'internal'}
            ]
        else:
            return [
                {'day': 0, 'action': 'automated_reminder', 'channel': 'email'},
                {'day': 7, 'action': 'second_reminder', 'channel': 'email'},
                {'day': 14, 'action': 'personal_outreach', 'channel': 'phone'}
            ]
    
    def _determine_automation(self, risk_level: RiskLevel) -> str:
        """Determine level of automation"""
        automation_map = {
            RiskLevel.LOW: 'full_automation',
            RiskLevel.MEDIUM: 'supervised_automation',
            RiskLevel.HIGH: 'manual_review_required',
            RiskLevel.CRITICAL: 'manual_only'
        }
        return automation_map.get(risk_level, 'supervised_automation')

class ARCashApplicationAI:
    """AI-powered cash application and reconciliation"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def match_payment_to_invoices(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Intelligently match payments to invoices"""
        
        matches = []
        confidence_scores = []
        
        # Extract payment information
        amount = payment_data.get('amount', 0)
        reference = payment_data.get('reference', '')
        customer_info = payment_data.get('customer_info', '')
        
        # Find potential invoice matches
        potential_invoices = self._find_potential_matches(amount, reference, customer_info)
        
        for invoice in potential_invoices:
            confidence = self._calculate_match_confidence(payment_data, invoice)
            if confidence > 0.7:
                matches.append({
                    'invoice_id': invoice['id'],
                    'invoice_number': invoice['number'],
                    'confidence': confidence,
                    'match_type': self._determine_match_type(confidence),
                    'suggested_amount': min(amount, invoice['balance'])
                })
        
        return {
            'payment_id': payment_data.get('id'),
            'total_amount': amount,
            'matches': sorted(matches, key=lambda x: x['confidence'], reverse=True),
            'auto_apply': len(matches) == 1 and matches[0]['confidence'] > 0.95,
            'requires_review': len(matches) == 0 or max([m['confidence'] for m in matches]) < 0.8
        }
    
    def _find_potential_matches(self, amount: float, reference: str, customer_info: str) -> List[Dict]:
        """Find potential invoice matches"""
        # In production, query database for matching invoices
        return [
            {'id': 1, 'number': 'INV-001', 'balance': amount, 'customer': 'ABC Corp'},
            {'id': 2, 'number': 'INV-002', 'balance': amount * 0.5, 'customer': 'ABC Corp'}
        ]
    
    def _calculate_match_confidence(self, payment_data: Dict, invoice_data: Dict) -> float:
        """Calculate confidence score for payment-invoice match"""
        confidence = 0.0
        
        # Exact amount match
        if abs(payment_data.get('amount', 0) - invoice_data.get('balance', 0)) < 0.01:
            confidence += 0.4
        
        # Reference number match
        if invoice_data.get('number', '') in payment_data.get('reference', ''):
            confidence += 0.3
        
        # Customer match
        if invoice_data.get('customer', '').lower() in payment_data.get('customer_info', '').lower():
            confidence += 0.2
        
        # Date proximity
        confidence += 0.1  # Base score for date proximity
        
        return min(1.0, confidence)
    
    def _determine_match_type(self, confidence: float) -> str:
        """Determine type of match based on confidence"""
        if confidence >= 0.95:
            return 'exact_match'
        elif confidence >= 0.8:
            return 'high_confidence'
        elif confidence >= 0.6:
            return 'probable_match'
        else:
            return 'possible_match'