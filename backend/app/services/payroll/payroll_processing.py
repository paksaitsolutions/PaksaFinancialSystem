    def _calculate_overtime_pay(
        """ Calculate Overtime Pay."""
        self, overtime_hours: Decimal, pay_rate: Decimal, pay_type: str
    ) -> Decimal:
        """ Calculate Overtime Pay."""
        """Calculate overtime pay based on hours worked and pay rate/type."""
        if overtime_hours <= 0:
            return Decimal("0.00")
            
        if pay_type == "HOURLY":
            # Calculate overtime at time-and-a-half rate
            overtime_rate = pay_rate * Decimal("1.5")
            return (overtime_hours * overtime_rate).quantize(Decimal("0.01"), ROUND_HALF_UP)
        else:  # SALARIED
            # For salaried employees, check if they are overtime exempt
            if getattr(employee, 'is_overtime_exempt', True):
                return Decimal("0.00")
            # Calculate equivalent hourly rate for salaried employees
            hourly_rate = pay_rate / (settings.HOURS_PER_PAY_PERIOD or 80)
            overtime_rate = hourly_rate * Decimal("1.5")
            return (overtime_hours * overtime_rate).quantize(Decimal("0.01"), ROUND_HALF_UP)

    def _calculate_earnings(
        """ Calculate Earnings."""
        self, 
        employee: Employee, 
        pay_period: PayPeriod,
        regular_pay: Decimal,
        overtime_pay: Decimal
    ) -> List[Dict]:
        """ Calculate Earnings."""
        """
        Calculate all earnings for an employee for the pay period.
        
        Args:
            employee: The employee
            pay_period: The pay period
            regular_pay: Calculated regular pay amount
            overtime_pay: Calculated overtime pay amount
            
        Returns:
            List of earning dictionaries with amount and metadata
        """
        earnings = []
        
        # Add base salary/wage
        earnings.append({
            "type": "REGULAR",
            "name": "Regular Pay",
            "amount": regular_pay,
            "is_taxable": True,
            "gl_account_code": "5000"  # Salary Expense
        })
        
        # Add overtime pay if any
        if overtime_pay > 0:
            earnings.append({
                "type": "OVERTIME",
                "name": "Overtime Pay",
                "amount": overtime_pay,
                "is_taxable": True,
                "gl_account_code": "5001"  # Overtime Expense
            })
        
        # Add other earnings (bonuses, commissions, etc.)
        other_earnings = self._get_other_earnings(employee, pay_period)
        earnings.extend(other_earnings)
        
        return earnings
    
    def _get_other_earnings(
        """ Get Other Earnings."""
        self, employee: Employee, pay_period: PayPeriod
    ) -> List[Dict]:
        """ Get Other Earnings."""
        """
        Get other earnings like bonuses, commissions, etc.
        
        Args:
            employee: The employee
            pay_period: The pay period
            
        Returns:
            List of earning dictionaries
        """
        earnings = []
        
        # Get one-time bonuses
        bonuses = (
            self.db.query(EmployeeEarning)
            .filter(
                EmployeeEarning.employee_id == employee.id,
                EmployeeEarning.is_active == True,
                EmployeeEarning.effective_date <= pay_period.end_date,
                or_(
                    EmployeeEarning.end_date.is_(None),
                    EmployeeEarning.end_date >= pay_period.start_date
                ),
                EmployeeEarning.earning_type.in_(["BONUS", "COMMISSION", "OTHER"])
            )
            .all()
        )
        
        for bonus in bonuses:
            amount = bonus.amount
            
            # For commissions, calculate based on sales if needed
            if bonus.calculation_type == "PERCENTAGE" and bonus.rate:
                sales_amount = self._get_sales_amount(employee.id, pay_period, bonus)
                amount = (sales_amount * (bonus.rate / 100)).quantize(Decimal("0.01"), ROUND_HALF_UP)
            
            earnings.append({
                "type": bonus.earning_type,
                "name": bonus.name,
                "amount": amount,
                "is_taxable": not bonus.is_tax_exempt,
                "gl_account_code": bonus.gl_account_code or "5060"  # Other Compensation Expense
            })
        
        return earnings
    
    def _get_sales_amount(
        """ Get Sales Amount."""
        self, 
        employee_id: UUID, 
        pay_period: PayPeriod,
        bonus: EmployeeEarning
    ) -> Decimal:
        """ Get Sales Amount."""
        """
        Get sales amount for commission calculation.
        
        Args:
            employee_id: ID of the employee
            pay_period: The pay period
            bonus: The bonus/commission earning record
            
        Returns:
            Total sales amount for the period
        """
        # In a real implementation, this would query the sales/orders system
        # to get the total sales amount for the employee for the pay period
        # For now, return a placeholder value
        return Decimal("0.00")
    
    def _calculate_pre_tax_deductions(
        """ Calculate Pre Tax Deductions."""
        self, 
        employee: Employee, 
        pay_period: PayPeriod,
        earnings: List[Dict]
    ) -> List[Dict]:
        """ Calculate Pre Tax Deductions."""
        """
        Calculate pre-tax deductions (retirement, benefits, etc.).
        
        Args:
            employee: The employee
            pay_period: The pay period
            earnings: List of employee earnings for the period
            
        Returns:
            List of deduction dictionaries
        """
        deductions = []
        
        # Get employee's active benefit enrollments
        enrollments = (
            self.db.query(BenefitEnrollment)
            .join(BenefitPlan)
            .filter(
                BenefitEnrollment.employee_id == employee.id,
                BenefitEnrollment.is_active == True,
                BenefitPlan.is_pre_tax == True,
                BenefitEnrollment.effective_date <= pay_period.end_date,
                or_(
                    BenefitEnrollment.termination_date.is_(None),
                    BenefitEnrollment.termination_date >= pay_period.start_date
                )
            )
            .all()
        )
        
        for enrollment in enrollments:
            benefit = enrollment.benefit_plan
            
            # Calculate deduction amount based on benefit type
            if benefit.calculation_type == "FIXED_AMOUNT":
                amount = benefit.amount or Decimal("0.00")
            elif benefit.calculation_type == "PERCENTAGE_OF_GROSS":
                gross_pay = sum(e["amount"] for e in earnings if e["is_taxable"])
                amount = (gross_pay * (benefit.rate / 100)).quantize(Decimal("0.01"), ROUND_HALF_UP)
            else:
                amount = Decimal("0.00")
            
            # Apply annual maximum if set
            if benefit.annual_max:
                ytd_deductions = self._get_ytd_deductions(
                    employee.id, 
                    benefit.id, 
                    pay_period.end_date.year
                )
                remaining = max(Decimal("0.00"), benefit.annual_max - ytd_deductions)
                amount = min(amount, remaining)
            
            if amount > 0:
                deductions.append({
                    "type": "BENEFIT",
                    "name": benefit.name,
                    "amount": amount,
                    "is_pre_tax": True,
                    "benefit_plan_id": benefit.id,
                    "gl_account_code": benefit.expense_gl_account or "6020"  # Employee Benefits
                })
        
        return deductions
    
    def _get_ytd_deductions(
        """ Get Ytd Deductions."""
        self, 
        employee_id: UUID, 
        benefit_plan_id: UUID,
        year: int
    ) -> Decimal:
        """ Get Ytd Deductions."""
        """
        Get year-to-date deductions for a benefit plan.
        
        Args:
            employee_id: ID of the employee
            benefit_plan_id: ID of the benefit plan
            year: Calendar year
            
        Returns:
            Total YTD deductions for the benefit plan
        """
        # In a real implementation, this would query the deductions history
        # For now, return a placeholder value
        return Decimal("0.00")
