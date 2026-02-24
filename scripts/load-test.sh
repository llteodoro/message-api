#!/bin/bash

# Message API Load Testing Script
# Performs basic load testing and performance monitoring

set -euo pipefail

# Configuration
BASE_URL="${BASE_URL:-http://localhost:8000}"
CONCURRENT_USERS="${CONCURRENT_USERS:-10}"
DURATION="${DURATION:-60}"
REQUESTS_OUTPUT="${REQUESTS_OUTPUT:-load-test-results.txt}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

test_health() {
    log_info "Testing API health..."
    RESPONSE=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL/health")
    
    if [ "$RESPONSE" = "200" ]; then
        log_info "✓ API is healthy (HTTP $RESPONSE)"
    else
        log_error "API is not responding correctly (HTTP $RESPONSE)"
        exit 1
    fi
}

create_test_messages() {
    log_info "Creating test messages..."
    
    for i in {1..5}; do
        curl -s -X POST "$BASE_URL/messages" \
            -H "Content-Type: application/json" \
            -d "{\"text\": \"Load test message $i - $(date +%s)\"}" > /dev/null
        
        log_info "Created message $i/5"
    done
    
    log_info "Test messages created"
}

load_test_get_all() {
    log_info "Load testing GET /messages with $CONCURRENT_USERS concurrent users for $DURATION seconds..."
    
    local start_time=$(date +%s)
    local request_count=0
    local success_count=0
    local error_count=0
    local total_response_time=0
    
    # Cleanup previous results
    > "$REQUESTS_OUTPUT"
    
    for ((i=0; i<CONCURRENT_USERS; i++)); do
        (
            while true; do
                local current_time=$(date +%s)
                local elapsed=$((current_time - start_time))
                
                if [ $elapsed -ge $DURATION ]; then
                    break
                fi
                
                local response_time=$(curl -s -w "%{time_total}" -o /dev/null -w "%{http_code}" "$BASE_URL/messages")
                local http_code="${response_time: -3}"
                local time_taken="${response_time%???}"
                
                echo "$(date +%s.%N) $http_code $time_taken" >> "$REQUESTS_OUTPUT"
                
                if [ "$http_code" = "200" ]; then
                    ((success_count++))
                else
                    ((error_count++))
                fi
                ((request_count++))
            done
        ) &
    done
    
    # Wait for all background jobs
    wait
    
    # Analyze results
    analyze_results
}

load_test_create() {
    log_info "Load testing POST /messages with $CONCURRENT_USERS concurrent users for $DURATION seconds..."
    
    local start_time=$(date +%s)
    local request_count=0
    local success_count=0
    local error_count=0
    
    > "$REQUESTS_OUTPUT"
    
    for ((i=0; i<CONCURRENT_USERS; i++)); do
        (
            while true; do
                local current_time=$(date +%s)
                local elapsed=$((current_time - start_time))
                
                if [ $elapsed -ge $DURATION ]; then
                    break
                fi
                
                local msg="Load test $i-$request_count at $(date +%s%N)"
                local response_time=$(curl -s -X POST "$BASE_URL/messages" \
                    -H "Content-Type: application/json" \
                    -d "{\"text\": \"$msg\"}" \
                    -w "%{time_total} %{http_code}" -o /dev/null)
                
                echo "$(date +%s.%N) $response_time" >> "$REQUESTS_OUTPUT"
                
                ((request_count++))
            done
        ) &
    done
    
    wait
    
    analyze_results
}

analyze_results() {
    log_info "Analyzing results..."
    
    if [ ! -f "$REQUESTS_OUTPUT" ]; then
        log_error "No results file found"
        return
    fi
    
    local total_requests=$(wc -l < "$REQUESTS_OUTPUT")
    local successful=$(grep " 20[0-9] " "$REQUESTS_OUTPUT" | wc -l || echo 0)
    local failed=$((total_requests - successful))
    local success_rate=$((successful * 100 / total_requests))
    
    echo ""
    echo -e "${GREEN}=== Load Test Results ===${NC}"
    echo "Total Requests: $total_requests"
    echo "Successful: $successful"
    echo "Failed: $failed"
    echo "Success Rate: $success_rate%"
    
    # Response time analysis
    if grep -q "^[0-9]" "$REQUESTS_OUTPUT"; then
        local avg_response=$(awk '{sum+=$3; count++} END {print sum/count}' "$REQUESTS_OUTPUT")
        echo "Average Response Time: ${avg_response}s"
    fi
    
    echo ""
}

benchmark() {
    log_info "Running benchmark..."
    
    # Simple benchmark - measure endpoint response times
    echo -e "${GREEN}=== Endpoint Benchmarks ===${NC}"
    
    for endpoint in "health" "messages" "metrics"; do
        local response_time=$(curl -s -w "%{time_total}" -o /dev/null "$BASE_URL/$endpoint")
        echo "$endpoint: ${response_time}s"
    done
    
    echo ""
}

show_metrics() {
    log_info "Fetching API metrics..."
    
    echo -e "${GREEN}=== API Metrics ===${NC}"
    curl -s "$BASE_URL/metrics" | head -20
    
    echo ""
}

usage() {
    cat << EOF
Usage: $0 [COMMAND] [OPTIONS]

Commands:
  health            - Test API health
  create            - Create test messages
  load-get          - Load test GET /messages
  load-post         - Load test POST /messages
  benchmark         - Run endpoint benchmarks
  metrics           - Show API metrics
  full              - Run full test suite

Options:
  -u, --url URL                Base URL (default: http://localhost:8000)
  -c, --concurrent USERS       Concurrent users (default: 10)
  -d, --duration SECONDS       Test duration (default: 60)
  
Examples:
  $0 health
  $0 load-get -c 20 -d 120
  $0 full -u http://api.example.com

EOF
}

main() {
    case "${1:-full}" in
        health)
            test_health
            ;;
        create)
            create_test_messages
            ;;
        load-get)
            load_test_get_all
            ;;
        load-post)
            load_test_create
            ;;
        benchmark)
            benchmark
            ;;
        metrics)
            show_metrics
            ;;
        full)
            test_health
            create_test_messages
            benchmark
            show_metrics
            load_test_get_all
            ;;
        -h|--help)
            usage
            ;;
        *)
            log_error "Unknown command: $1"
            usage
            exit 1
            ;;
    esac
}

main "$@"
