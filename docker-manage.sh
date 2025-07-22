#!/bin/bash

# Docker Compose Management Script for TRS Project
# This script helps manage both the main application and Airflow services

set -e

MAIN_COMPOSE="docker-compose.yml"
AIRFLOW_COMPOSE="docker-compose.airflow.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

usage() {
    echo "Usage: $0 {up|down|restart|logs|status} [main|airflow|all]"
    echo ""
    echo "Commands:"
    echo "  up        - Start services"
    echo "  down      - Stop services"
    echo "  restart   - Restart services"
    echo "  logs      - Show logs"
    echo "  status    - Show service status"
    echo "  init      - Initialize Airflow (run once)"
    echo ""
    echo "Services:"
    echo "  main      - Main application (PostgreSQL + Qdrant)"
    echo "  airflow   - Airflow orchestration services"
    echo "  all       - Both main and airflow (default)"
    echo ""
    echo "Examples:"
    echo "  $0 up                 # Start all services"
    echo "  $0 up main            # Start only main application"
    echo "  $0 up airflow         # Start only Airflow"
    echo "  $0 init               # Initialize Airflow database"
    echo "  $0 logs airflow       # Show Airflow logs"
    echo "  $0 status             # Show status of all services"
}

get_compose_files() {
    local service=$1
    case $service in
        "main")
            echo "-f $MAIN_COMPOSE"
            ;;
        "airflow")
            echo "-f $AIRFLOW_COMPOSE"
            ;;
        "all"|"")
            echo "-f $MAIN_COMPOSE -f $AIRFLOW_COMPOSE"
            ;;
        *)
            echo -e "${RED}Error: Invalid service '$service'. Use 'main', 'airflow', or 'all'${NC}"
            exit 1
            ;;
    esac
}

cmd_up() {
    local service=${1:-all}
    local compose_files=$(get_compose_files $service)

    echo -e "${GREEN}Starting $service services...${NC}"
    docker compose $compose_files up -d
    echo -e "${GREEN}✅ $service services started${NC}"
}

cmd_down() {
    local service=${1:-all}
    local compose_files=$(get_compose_files $service)

    echo -e "${YELLOW}Stopping $service services...${NC}"
    docker compose $compose_files down
    echo -e "${YELLOW}✅ $service services stopped${NC}"
}

cmd_restart() {
    local service=${1:-all}
    echo -e "${YELLOW}Restarting $service services...${NC}"
    cmd_down $service
    cmd_up $service
}

cmd_logs() {
    local service=${1:-all}
    local compose_files=$(get_compose_files $service)

    echo -e "${GREEN}Showing logs for $service services...${NC}"
    docker compose $compose_files logs -f
}

cmd_status() {
    local service=${1:-all}
    local compose_files=$(get_compose_files $service)

    echo -e "${GREEN}Status of $service services:${NC}"
    docker compose $compose_files ps
}

cmd_init() {
    echo -e "${GREEN}Initializing Airflow...${NC}"
    echo -e "${YELLOW}This will:"
    echo "  - Set up Airflow database"
    echo "  - Create admin user (airflow/airflow)"
    echo "  - Initialize required directories${NC}"
    echo ""

    # Make sure directories exist
    mkdir -p ./airflow/{dags,logs,plugins,config}

    # Initialize Airflow
    docker compose -f $AIRFLOW_COMPOSE up airflow-init

    echo -e "${GREEN}✅ Airflow initialization complete!${NC}"
    echo -e "${GREEN}You can now start Airflow with: $0 up airflow${NC}"
}

# Main script logic
case $1 in
    "up")
        cmd_up $2
        ;;
    "down")
        cmd_down $2
        ;;
    "restart")
        cmd_restart $2
        ;;
    "logs")
        cmd_logs $2
        ;;
    "status")
        cmd_status $2
        ;;
    "init")
        cmd_init
        ;;
    *)
        usage
        exit 1
        ;;
esac
