"""
End-to-end financial scenario tests for core workflows.
"""

from datetime import date


class TestFinancialScenarios:
    def test_monthly_close(self, client):
        status_response = client.get("/api/v1/gl/period-close/status")
        assert status_response.status_code == 200

        close_response = client.post(
            "/api/v1/gl/period-close/close",
            json={"period": "December 2024", "approved_by": "Finance Lead"},
        )
        assert close_response.status_code == 200
        assert close_response.json().get("success") is True

    def test_vendor_payment_cycle(self, client):
        vendors_response = client.get("/api/v1/ap/vendors")
        assert vendors_response.status_code == 200
        vendor_records = vendors_response.json().get("data", [])
        vendor_id = vendor_records[0]["id"] if vendor_records else None

        if not vendor_id:
            create_vendor = client.post(
                "/api/v1/ap/vendors",
                json={"name": "Scenario Vendor", "email": "scenario@vendor.local"},
            )
            assert create_vendor.status_code in [200, 409]
            vendors_response = client.get("/api/v1/ap/vendors")
            vendor_records = vendors_response.json().get("data", [])
            vendor_id = vendor_records[0]["id"] if vendor_records else None

        assert vendor_id is not None

        invoice_response = client.post(
            "/api/v1/ap/invoices",
            json={"vendor_id": vendor_id, "total_amount": 1500},
        )
        assert invoice_response.status_code == 200

        payment_response = client.post(
            "/api/v1/ap/payments",
            json={
                "vendor_id": vendor_id,
                "amount": 1500,
                "payment_method": "check",
                "reference": "E2E-AP-001",
            },
        )
        assert payment_response.status_code == 200

    def test_tax_filing(self, client):
        response = client.post(
            "/tax/returns",
            json={
                "return_type": "sales_tax",
                "period_start": date(2024, 1, 1).isoformat(),
                "period_end": date(2024, 3, 31).isoformat(),
                "jurisdiction": "CA",
                "amount_due": 2500,
            },
        )
        assert response.status_code == 200
