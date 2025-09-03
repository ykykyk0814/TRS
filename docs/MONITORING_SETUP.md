# Monitoring Setup Guide

This document describes the monitoring infrastructure for the Travel Recommendation System using Prometheus, Grafana, and various exporters.

## Overview

The monitoring stack consists of:
- **Prometheus**: Time-series database for metrics collection
- **Grafana**: Visualization and dashboard platform
- **Node Exporter**: Host system metrics
- **cAdvisor**: Container metrics
- **PostgreSQL Exporter**: Database metrics
- **Redis Exporter**: Redis metrics

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │     Airflow     │    │     Qdrant      │
│   (Port 8000)   │    │   (Port 8080)   │    │   (Port 6333)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Prometheus    │
                    │   (Port 9090)   │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │     Grafana     │
                    │   (Port 3000)   │
                    └─────────────────┘
```

## Quick Start

### 1. Initial Setup

```bash
# Run the setup command to create necessary directories and networks
./scripts/manage_monitoring.sh setup
```

### 2. Start Monitoring Services

```bash
# Start all monitoring services
./scripts/manage_monitoring.sh start
```

### 3. Access Services

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **Node Exporter**: http://localhost:9100
- **cAdvisor**: http://localhost:8081
- **PostgreSQL Exporter**: http://localhost:9187
- **Redis Exporter**: http://localhost:9121

## Configuration Files

### Prometheus Configuration (`monitoring/prometheus/prometheus.yml`)

The main Prometheus configuration includes:
- Global scrape intervals (15s)
- Service discovery for all components
- Alerting rules
- Metrics retention (200 hours)

### Alerting Rules (`monitoring/prometheus/rules/alerts.yml`)

Pre-configured alerts for:
- Service availability
- Database performance
- Resource usage (CPU, Memory, Disk)
- Container health
- Airflow DAG failures

### Grafana Configuration

- **Datasources**: Automatic Prometheus connection
- **Dashboards**: Pre-configured travel recommendation system overview

## Management Commands

```bash
# Start monitoring services
./scripts/manage_monitoring.sh start

# Stop monitoring services
./scripts/manage_monitoring.sh stop

# Restart monitoring services
./scripts/manage_monitoring.sh restart

# Check service status
./scripts/manage_monitoring.sh status

# View logs
./scripts/manage_monitoring.sh logs [service_name]

# Health check
./scripts/manage_monitoring.sh health

# Show help
./scripts/manage_monitoring.sh
```

## Metrics Collected

### System Metrics (Node Exporter)
- CPU usage
- Memory usage
- Disk usage
- Network statistics
- File system metrics

### Container Metrics (cAdvisor)
- Container CPU usage
- Container memory usage
- Container network I/O
- Container disk I/O

### Database Metrics (PostgreSQL Exporter)
- Active connections
- Query performance
- Database size
- Lock statistics
- Transaction metrics

### Redis Metrics (Redis Exporter)
- Memory usage
- Connection count
- Command statistics
- Key statistics

### Application Metrics
- FastAPI application health
- Airflow DAG status
- Qdrant vector database metrics

## Dashboards

### Travel Recommendation System Overview

The main dashboard includes:
1. **System Overview**: Service status indicators
2. **CPU Usage**: Real-time CPU utilization
3. **Memory Usage**: Memory consumption trends
4. **Disk Usage**: Storage utilization
5. **Database Connections**: Active database connections
6. **Redis Memory**: Redis memory usage
7. **Container Metrics**: Docker container performance
8. **Application Health**: Service availability

## Customization

### Adding New Metrics

1. **Create a new exporter** or use existing ones
2. **Add to Prometheus config** in `monitoring/prometheus/prometheus.yml`
3. **Create Grafana panels** for visualization
4. **Set up alerts** if needed

### Modifying Alerts

Edit `monitoring/prometheus/rules/alerts.yml` to:
- Adjust thresholds
- Add new alert conditions
- Modify alert severity levels

### Adding New Dashboards

1. Create dashboard JSON files in `monitoring/grafana/provisioning/dashboards/`
2. Restart Grafana or use the UI to import

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 9090, 3000, 9100, 8081, 9187, 9121 are available
2. **Network issues**: Check if the `monitoring` Docker network exists
3. **Permission issues**: Ensure Docker has access to host directories

### Health Checks

```bash
# Check all services health
./scripts/manage_monitoring.sh health

# Check specific service logs
./scripts/manage_monitoring.sh logs prometheus
```

### Logs

```bash
# View all monitoring service logs
./scripts/manage_monitoring.sh logs

# View specific service logs
./scripts/manage_monitoring.sh logs grafana
```

## Integration with Existing Services

### FastAPI Application

To expose metrics from your FastAPI application:

1. Install `prometheus-client`:
```bash
pip install prometheus-client
```

2. Add metrics endpoint to your FastAPI app:
```python
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI

app = FastAPI()

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

### Airflow

Airflow provides built-in metrics at `/metrics` endpoint when configured with:
```yaml
AIRFLOW__METRICS__STATSD_ON: 'true'
AIRFLOW__METRICS__STATSD_HOST: localhost
AIRFLOW__METRICS__STATSD_PORT: 8125
```

## Security Considerations

- **Default credentials**: Change default Grafana admin password
- **Network isolation**: Use Docker networks for service communication
- **Access control**: Restrict access to monitoring endpoints in production
- **TLS**: Enable HTTPS for production deployments

## Performance Tuning

### Prometheus
- Adjust scrape intervals based on metric update frequency
- Configure retention policies based on storage requirements
- Use recording rules for complex queries

### Grafana
- Optimize dashboard queries
- Use appropriate time ranges
- Implement dashboard caching

## Next Steps

1. **Set up alerting**: Configure AlertManager for notifications
2. **Add custom metrics**: Instrument your application code
3. **Create specialized dashboards**: Build dashboards for specific use cases
4. **Set up log aggregation**: Integrate with ELK stack or similar
5. **Performance testing**: Monitor system under load

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review service logs
3. Verify configuration files
4. Check Docker network connectivity 
