def test_employee_model():
    from .models import Employee
    emp = Employee(id=1, name='John Doe', position='Manager', salary=5000.0)
    assert emp.name == 'John Doe'
    assert emp.position == 'Manager'
    assert emp.salary == 5000.0

def test_payroll_record_model():
    from .models import PayrollRecord
    record = PayrollRecord(id=1, employee_id=1, pay_date='2025-03-01', gross_pay=5000.0, deductions=500.0, net_pay=4500.0)
    assert record.gross_pay == 5000.0
    assert record.net_pay == 4500.0
