"""
Test script for dashboard system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.services.dashboard_service import *
from datetime import datetime

# Connect to database
engine = create_engine('sqlite:///paksa_complete.db')
Session = sessionmaker(bind=engine)
db = Session()

def test_dashboard_system():
    """Test dashboard system functionality"""
    print("=== Testing Dashboard System ===")
    
    # Test KPI generation
    print("1. Testing KPI generation...")
    try:
        kpis = DashboardService.get_financial_kpis(db)
        print(f"   Generated {len(kpis)} KPIs:")
        for key, kpi in kpis.items():
            print(f"     {kpi['label']}: {kpi['value']} ({kpi['trend']})")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test chart data generation
    print("2. Testing chart data generation...")
    try:
        chart_types = ['revenue_trend', 'expense_breakdown', 'cash_flow', 'ap_aging', 'ar_aging']
        for chart_type in chart_types:
            chart_data = DashboardService.get_chart_data(db, chart_type)
            print(f"   {chart_type}: {len(chart_data.get('labels', []))} data points")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test alerts
    print("3. Testing alert system...")
    try:
        alerts = AlertService.get_active_alerts(db, 'test-user')
        print(f"   Generated {len(alerts)} alerts:")
        for alert in alerts:
            print(f"     {alert['type']}: {alert['title']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test quick actions
    print("4. Testing quick actions...")
    try:
        actions = QuickActionsService.get_quick_actions(db, 'test-user')
        print(f"   Available {len(actions)} quick actions:")
        for action in actions:
            print(f"     {action['title']}: {action['url']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test activity feed
    print("5. Testing activity feed...")
    try:
        activities = ActivityFeedService.get_recent_activity(db, 'test-user', 10)
        print(f"   Retrieved {len(activities)} recent activities:")
        for activity in activities[:3]:  # Show first 3
            print(f"     {activity['type']}: {activity['title']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test financial ratios
    print("6. Testing financial ratios...")
    try:
        ratios = DashboardMetrics.calculate_financial_ratios(db)
        print(f"   Calculated {len(ratios)} financial ratios:")
        for key, ratio in ratios.items():
            print(f"     {ratio['label']}: {ratio['value']} ({ratio['status']})")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test performance indicators
    print("7. Testing performance indicators...")
    try:
        indicators = DashboardMetrics.get_performance_indicators(db)
        print(f"   Generated {len(indicators)} performance indicators:")
        for key, indicator in indicators.items():
            print(f"     {indicator['label']}: {indicator['value']} days")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("=== Dashboard System Test Complete ===")

if __name__ == "__main__":
    test_dashboard_system()
    db.close()