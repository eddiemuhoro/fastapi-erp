#!/bin/bash

# FastAPI ERP System - cURL Examples
# This script demonstrates various API calls using cURL

# Configuration
BASE_URL="http://localhost:8000"
API_VERSION="v1"
API_BASE="${BASE_URL}/api/${API_VERSION}"

echo "🚀 FastAPI ERP System - cURL Examples"
echo "====================================="
echo "Base URL: ${BASE_URL}"
echo ""

# Function to make pretty JSON output
pretty_json() {
    if command -v jq >/dev/null 2>&1; then
        jq '.'
    else
        python3 -m json.tool
    fi
}

# Function to check if server is running
check_server() {
    echo "🔍 Checking if server is running..."
    if curl -s "${BASE_URL}/health" > /dev/null; then
        echo "✅ Server is running"
        echo ""
    else
        echo "❌ Server is not running. Please start the FastAPI server first:"
        echo "   python app.py"
        exit 1
    fi
}

# Authentication Examples
auth_examples() {
    echo "🔐 Authentication Examples"
    echo "========================="
    
    echo ""
    echo "📋 1. User Login"
    echo "----------------"
    echo "Request:"
    echo "curl -X POST \"${API_BASE}/auth/login\" \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -d '{\"username\": \"admin\", \"password\": \"password\"}'"
    echo ""
    echo "Response:"
    curl -X POST "${API_BASE}/auth/login" \
      -H "Content-Type: application/json" \
      -d '{"username": "admin", "password": "password"}' \
      -s | pretty_json
    echo ""
    
    echo "📋 2. Get Current User (if session-based auth implemented)"
    echo "---------------------------------------------------------"
    echo "Request:"
    echo "curl -X GET \"${API_BASE}/auth/me\""
    echo ""
    echo "Response:"
    curl -X GET "${API_BASE}/auth/me" -s | pretty_json
    echo ""
}

# Reports Examples
reports_examples() {
    echo "📊 Reports Examples"
    echo "=================="
    
    echo ""
    echo "📈 1. Today's Hourly Sales"
    echo "-------------------------"
    echo "Request:"
    echo "curl -X POST \"${API_BASE}/reports/sales\" \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -d '{\"category\": \"today_hourly\"}'"
    echo ""
    echo "Response:"
    curl -X POST "${API_BASE}/reports/sales" \
      -H "Content-Type: application/json" \
      -d '{"category": "today_hourly"}' \
      -s | pretty_json
    echo ""
    
    echo "📈 2. Sales by Representative"
    echo "----------------------------"
    echo "Request:"
    echo "curl -X POST \"${API_BASE}/reports/sales\" \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -d '{\"category\": \"rep\", \"fromdate\": \"2024-01-01\", \"todate\": \"2024-12-31\"}'"
    echo ""
    echo "Response:"
    curl -X POST "${API_BASE}/reports/sales" \
      -H "Content-Type: application/json" \
      -d '{"category": "rep", "fromdate": "2024-01-01", "todate": "2024-12-31"}' \
      -s | pretty_json
    echo ""
    
    echo "👥 3. Customer Balances"
    echo "----------------------"
    echo "Request:"
    echo "curl -X POST \"${API_BASE}/reports/customers\" \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -d '{\"category\": \"customer_balances\", \"as_of_date\": \"2024-12-31\"}'"
    echo ""
    echo "Response:"
    curl -X POST "${API_BASE}/reports/customers" \
      -H "Content-Type: application/json" \
      -d '{"category": "customer_balances", "as_of_date": "2024-12-31"}' \
      -s | pretty_json
    echo ""
    
    echo "📦 4. Inventory Summary"
    echo "----------------------"
    echo "Request:"
    echo "curl -X POST \"${API_BASE}/reports/inventory\" \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -d '{\"category\": \"summary\"}'"
    echo ""
    echo "Response:"
    curl -X POST "${API_BASE}/reports/inventory" \
      -H "Content-Type: application/json" \
      -d '{"category": "summary"}' \
      -s | pretty_json
    echo ""
    
    echo "📦 5. Low Stock Items"
    echo "--------------------"
    echo "Request:"
    echo "curl -X POST \"${API_BASE}/reports/inventory\" \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -d '{\"category\": \"low_stock\", \"threshold\": 10}'"
    echo ""
    echo "Response:"
    curl -X POST "${API_BASE}/reports/inventory" \
      -H "Content-Type: application/json" \
      -d '{"category": "low_stock", "threshold": 10}' \
      -s | pretty_json
    echo ""
}

# CRUD Examples (if implemented)
crud_examples() {
    echo "🔧 CRUD Examples"
    echo "==============="
    
    echo ""
    echo "👥 1. List Customers"
    echo "-------------------"
    echo "Request:"
    echo "curl -X GET \"${API_BASE}/customers/\""
    echo ""
    echo "Response:"
    curl -X GET "${API_BASE}/customers/" -s | pretty_json
    echo ""
    
    echo "📦 2. List Inventory"
    echo "-------------------"
    echo "Request:"
    echo "curl -X GET \"${API_BASE}/inventory/\""
    echo ""
    echo "Response:"
    curl -X GET "${API_BASE}/inventory/" -s | pretty_json
    echo ""
    
    echo "🔍 3. Search Customers"
    echo "---------------------"
    echo "Request:"
    echo "curl -X GET \"${API_BASE}/customers/search?q=john\""
    echo ""
    echo "Response:"
    curl -X GET "${API_BASE}/customers/search?q=john" -s | pretty_json
    echo ""
}

# Error Examples
error_examples() {
    echo "❌ Error Handling Examples"
    echo "========================="
    
    echo ""
    echo "❌ 1. Invalid Login Credentials"
    echo "-------------------------------"
    echo "Request:"
    echo "curl -X POST \"${API_BASE}/auth/login\" \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -d '{\"username\": \"invalid\", \"password\": \"wrong\"}'"
    echo ""
    echo "Response:"
    curl -X POST "${API_BASE}/auth/login" \
      -H "Content-Type: application/json" \
      -d '{"username": "invalid", "password": "wrong"}' \
      -s | pretty_json
    echo ""
    
    echo "❌ 2. Invalid Report Category"
    echo "-----------------------------"
    echo "Request:"
    echo "curl -X POST \"${API_BASE}/reports/sales\" \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -d '{\"category\": \"invalid_category\"}'"
    echo ""
    echo "Response:"
    curl -X POST "${API_BASE}/reports/sales" \
      -H "Content-Type: application/json" \
      -d '{"category": "invalid_category"}' \
      -s | pretty_json
    echo ""
    
    echo "❌ 3. Missing Required Fields"
    echo "-----------------------------"
    echo "Request:"
    echo "curl -X POST \"${API_BASE}/reports/sales\" \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -d '{}'"
    echo ""
    echo "Response:"
    curl -X POST "${API_BASE}/reports/sales" \
      -H "Content-Type: application/json" \
      -d '{}' \
      -s | pretty_json
    echo ""
}

# Health Check Example
health_examples() {
    echo "🩺 Health Check Examples"
    echo "======================="
    
    echo ""
    echo "✅ 1. Health Check"
    echo "------------------"
    echo "Request:"
    echo "curl -X GET \"${BASE_URL}/health\""
    echo ""
    echo "Response:"
    curl -X GET "${BASE_URL}/health" -s | pretty_json
    echo ""
}

# API Documentation Examples
docs_examples() {
    echo "📚 API Documentation"
    echo "==================="
    
    echo ""
    echo "📖 Interactive Documentation (Swagger UI)"
    echo "------------------------------------------"
    echo "Open in browser: ${BASE_URL}/docs"
    echo ""
    
    echo "📖 Alternative Documentation (ReDoc)"
    echo "------------------------------------"
    echo "Open in browser: ${BASE_URL}/redoc"
    echo ""
    
    echo "📖 OpenAPI Schema (JSON)"
    echo "------------------------"
    echo "Request:"
    echo "curl -X GET \"${BASE_URL}/openapi.json\""
    echo ""
    echo "Response (truncated):"
    curl -X GET "${BASE_URL}/openapi.json" -s | jq '.info, .paths | keys' 2>/dev/null || echo "Install jq for better JSON viewing"
    echo ""
}

# Performance Testing Examples
performance_examples() {
    echo "⚡ Performance Testing Examples"
    echo "=============================="
    
    echo ""
    echo "🚀 1. Simple Load Test with cURL"
    echo "--------------------------------"
    echo "Run 10 concurrent requests:"
    echo ""
    echo "for i in {1..10}; do"
    echo "  curl -X POST \"${API_BASE}/reports/sales\" \\"
    echo "    -H \"Content-Type: application/json\" \\"
    echo "    -d '{\"category\": \"today_hourly\"}' \\"
    echo "    -w \"Response time: %{time_total}s\\n\" \\"
    echo "    -s -o /dev/null &"
    echo "done"
    echo "wait"
    echo ""
    
    echo "🚀 2. With Apache Bench (if installed)"
    echo "--------------------------------------"
    echo "ab -n 100 -c 10 -H \"Content-Type: application/json\" \\"
    echo "  -p <(echo '{\"category\": \"today_hourly\"}') \\"
    echo "  \"${API_BASE}/reports/sales\""
    echo ""
    
    echo "🚀 3. With wrk (if installed)"
    echo "-----------------------------"
    echo "wrk -t12 -c400 -d30s --script=post.lua \"${API_BASE}/reports/sales\""
    echo ""
    echo "Where post.lua contains:"
    echo "wrk.method = \"POST\""
    echo "wrk.body = '{\"category\": \"today_hourly\"}'"
    echo "wrk.headers[\"Content-Type\"] = \"application/json\""
    echo ""
}

# Main execution
main() {
    # Check if server is running
    check_server
    
    # Show examples based on command line argument
    case "${1:-all}" in
        "auth")
            auth_examples
            ;;
        "reports")
            reports_examples
            ;;
        "crud")
            crud_examples
            ;;
        "errors")
            error_examples
            ;;
        "health")
            health_examples
            ;;
        "docs")
            docs_examples
            ;;
        "performance")
            performance_examples
            ;;
        "all"|*)
            auth_examples
            reports_examples
            crud_examples
            error_examples
            health_examples
            docs_examples
            performance_examples
            ;;
    esac
    
    echo ""
    echo "🎉 Examples completed!"
    echo ""
    echo "💡 Tips:"
    echo "   - Install jq for better JSON formatting: sudo apt install jq"
    echo "   - Save responses to files: curl ... -o response.json"
    echo "   - Add -v flag for verbose output: curl -v ..."
    echo "   - Use -w flag for timing: curl -w \"Time: %{time_total}s\" ..."
    echo ""
    echo "📚 For more examples, visit: ${BASE_URL}/docs"
}

# Check command line arguments
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: $0 [category]"
    echo ""
    echo "Categories:"
    echo "  auth        - Authentication examples"
    echo "  reports     - Report generation examples"
    echo "  crud        - CRUD operation examples"
    echo "  errors      - Error handling examples"
    echo "  health      - Health check examples"
    echo "  docs        - Documentation examples"
    echo "  performance - Performance testing examples"
    echo "  all         - All examples (default)"
    echo ""
    echo "Examples:"
    echo "  $0 auth       # Show only authentication examples"
    echo "  $0 reports    # Show only report examples"
    echo "  $0            # Show all examples"
    exit 0
fi

# Run main function
main "$1"
