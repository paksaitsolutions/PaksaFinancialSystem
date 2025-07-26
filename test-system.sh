#!/bin/bash

# Paksa Financial System - Comprehensive System Test Script

echo "🧪 Paksa Financial System - Comprehensive Testing"
echo "================================================="

BASE_URL="http://localhost:8000/api/v1"
FRONTEND_URL="http://localhost:3000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to test API endpoint
test_endpoint() {
    local endpoint=$1
    local expected_status=$2
    local description=$3
    
    echo -n "Testing $description... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint")
    
    if [ "$response" -eq "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} ($response)"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC} (Expected: $expected_status, Got: $response)"
        ((TESTS_FAILED++))
    fi
}

# Function to test with authentication
test_auth_endpoint() {
    local endpoint=$1
    local expected_status=$2
    local description=$3
    local token=$4
    
    echo -n "Testing $description... "
    
    if [ -n "$token" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $token" "$BASE_URL$endpoint")
    else
        response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint")
    fi
    
    if [ "$response" -eq "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} ($response)"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC} (Expected: $expected_status, Got: $response)"
        ((TESTS_FAILED++))
    fi
}

echo ""
echo "🏥 Health Check Tests"
echo "===================="
test_endpoint "/health" 200 "System Health Check"
curl -s "$BASE_URL/health" | jq '.' 2>/dev/null || echo "Health check response received"

echo ""
echo "🔐 Authentication Tests"
echo "======================"
test_endpoint "/auth/login" 422 "Login endpoint (no data)"

# Try to get a token (this might fail if auth is not fully implemented)
echo -n "Attempting to get auth token... "
TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin123"}' 2>/dev/null)

if echo "$TOKEN_RESPONSE" | grep -q "access_token"; then
    TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.access_token' 2>/dev/null)
    echo -e "${GREEN}✅ Token obtained${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠️  Token not available (auth may need implementation)${NC}"
    TOKEN=""
fi

echo ""
echo "📊 General Ledger Tests"
echo "======================"
test_auth_endpoint "/gl/accounts" 200 "GL Accounts List" "$TOKEN"
test_auth_endpoint "/gl/journal-entries" 200 "Journal Entries List" "$TOKEN"

echo ""
echo "💰 Accounts Payable Tests"
echo "========================="
test_auth_endpoint "/ap/vendors" 200 "Vendors List" "$TOKEN"
test_auth_endpoint "/ap/bills" 200 "Bills List" "$TOKEN"

echo ""
echo "💳 Accounts Receivable Tests"
echo "============================"
test_auth_endpoint "/ar/customers" 200 "Customers List" "$TOKEN"
test_auth_endpoint "/ar/invoices" 200 "Invoices List" "$TOKEN"

echo ""
echo "📈 Budget Management Tests"
echo "=========================="
test_auth_endpoint "/budget/budgets" 200 "Budgets List" "$TOKEN"

echo ""
echo "💵 Cash Management Tests"
echo "========================"
test_auth_endpoint "/cash/accounts" 200 "Bank Accounts List" "$TOKEN"

echo ""
echo "👥 Human Resources Tests"
echo "========================"
test_auth_endpoint "/hrm/employees" 200 "Employees List" "$TOKEN"
test_auth_endpoint "/hrm/analytics" 200 "HR Analytics" "$TOKEN"

echo ""
echo "📦 Inventory Management Tests"
echo "============================="
test_auth_endpoint "/inventory/" 200 "Inventory Items List" "$TOKEN"

echo ""
echo "🤖 AI/BI Dashboard Tests"
echo "========================"
test_auth_endpoint "/bi/dashboards" 200 "BI Dashboards List" "$TOKEN"
test_auth_endpoint "/bi/analytics" 200 "BI Analytics" "$TOKEN"

echo ""
echo "🧠 AI Assistant Tests"
echo "====================="
test_auth_endpoint "/ai/configuration" 404 "AI Configuration" "$TOKEN"

echo ""
echo "🌐 Frontend Tests"
echo "================="
echo -n "Testing Frontend availability... "
frontend_response=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")
if [ "$frontend_response" -eq 200 ]; then
    echo -e "${GREEN}✅ PASS${NC} ($frontend_response)"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} (Got: $frontend_response)"
    ((TESTS_FAILED++))
fi

echo ""
echo "📊 Database Tests"
echo "================="
echo -n "Testing Database Connection... "
if docker-compose -f docker-compose.local-production.yml exec -T postgres pg_isready -U paksa_user -d paksa_financial_local > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((TESTS_FAILED++))
fi

echo -n "Testing Sample Data... "
SAMPLE_DATA=$(docker-compose -f docker-compose.local-production.yml exec -T postgres psql -U paksa_user -d paksa_financial_local -t -c "SELECT COUNT(*) FROM gl_account;" 2>/dev/null | tr -d ' ')
if [ "$SAMPLE_DATA" -gt 0 ] 2>/dev/null; then
    echo -e "${GREEN}✅ PASS${NC} ($SAMPLE_DATA accounts found)"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} (No sample data found)"
    ((TESTS_FAILED++))
fi

echo ""
echo "🔧 Redis Tests"
echo "=============="
echo -n "Testing Redis Connection... "
if docker-compose -f docker-compose.local-production.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((TESTS_FAILED++))
fi

echo ""
echo "📋 Test Summary"
echo "==============="
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo -e "Total Tests:  $((TESTS_PASSED + TESTS_FAILED))"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed! System is ready for use.${NC}"
    exit 0
else
    echo -e "\n${YELLOW}⚠️  Some tests failed. Check the system configuration.${NC}"
    exit 1
fi