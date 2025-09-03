#!/bin/bash

# Monitoring Management Script for Travel Recommendation System
# This script helps manage Prometheus, Grafana, and related monitoring services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to create external network if it doesn't exist
create_network() {
    if ! docker network ls | grep -q "monitoring"; then
        print_status "Creating external monitoring network..."
        docker network create monitoring
        print_success "Monitoring network created successfully"
    else
        print_status "Monitoring network already exists"
    fi
}

# Function to start monitoring services
start_monitoring() {
    print_status "Starting monitoring services..."

    # Create network first
    create_network

    # Start services
    docker-compose -f docker-compose.monitoring.yml up -d

    print_success "Monitoring services started successfully!"
    print_status "Services available at:"
    echo "  - Prometheus: http://localhost:9090"
    echo "  - Grafana: http://localhost:3000 (admin/admin)"
    echo "  - Node Exporter: http://localhost:9100"
    echo "  - cAdvisor: http://localhost:8081"
    echo "  - PostgreSQL Exporter: http://localhost:9187"
    echo "  - Redis Exporter: http://localhost:9121"
}

# Function to stop monitoring services
stop_monitoring() {
    print_status "Stopping monitoring services..."
    docker-compose -f docker-compose.monitoring.yml down
    print_success "Monitoring services stopped successfully!"
}

# Function to restart monitoring services
restart_monitoring() {
    print_status "Restarting monitoring services..."
    stop_monitoring
    sleep 2
    start_monitoring
}

# Function to show monitoring services status
status_monitoring() {
    print_status "Monitoring services status:"
    docker-compose -f docker-compose.monitoring.yml ps
}

# Function to show monitoring services logs
logs_monitoring() {
    local service=${1:-""}
    if [ -z "$service" ]; then
        print_status "Showing logs for all monitoring services..."
        docker-compose -f docker-compose.monitoring.yml logs -f
    else
        print_status "Showing logs for service: $service"
        docker-compose -f docker-compose.monitoring.yml logs -f "$service"
    fi
}

# Function to check monitoring services health
health_check() {
    print_status "Checking monitoring services health..."

    # Check Prometheus
    if curl -s http://localhost:9090/-/healthy > /dev/null; then
        print_success "Prometheus is healthy"
    else
        print_error "Prometheus is not responding"
    fi

    # Check Grafana
    if curl -s http://localhost:3000/api/health > /dev/null; then
        print_success "Grafana is healthy"
    else
        print_error "Grafana is not responding"
    fi

    # Check Node Exporter
    if curl -s http://localhost:9100/metrics > /dev/null; then
        print_success "Node Exporter is healthy"
    else
        print_error "Node Exporter is not responding"
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 {start|stop|restart|status|logs|health|setup}"
    echo ""
    echo "Commands:"
    echo "  start     - Start monitoring services"
    echo "  stop      - Stop monitoring services"
    echo "  restart   - Restart monitoring services"
    echo "  status    - Show status of monitoring services"
    echo "  logs      - Show logs (use: $0 logs [service_name])"
    echo "  health    - Check health of monitoring services"
    echo "  setup     - Initial setup of monitoring services"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 logs prometheus"
    echo "  $0 health"
}

# Function to perform initial setup
setup_monitoring() {
    print_status "Setting up monitoring services..."

    # Check Docker
    check_docker

    # Create network
    create_network

    # Create necessary directories
    mkdir -p monitoring/prometheus/rules
    mkdir -p monitoring/grafana/provisioning/{datasources,dashboards}

    print_success "Setup completed successfully!"
    print_status "You can now run '$0 start' to start the monitoring services"
}

# Main script logic
case "${1:-}" in
    start)
        check_docker
        start_monitoring
        ;;
    stop)
        check_docker
        stop_monitoring
        ;;
    restart)
        check_docker
        restart_monitoring
        ;;
    status)
        check_docker
        status_monitoring
        ;;
    logs)
        check_docker
        logs_monitoring "$2"
        ;;
    health)
        check_docker
        health_check
        ;;
    setup)
        setup_monitoring
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
