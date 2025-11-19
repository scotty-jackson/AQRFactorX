# Deployment Guide

Complete guide for deploying AQR Factor Explorer to production.

---

## Quick Start with Docker

The easiest way to run the entire stack:

```bash
# Start all services
make up

# Or manually:
docker-compose up -d

# Check logs
make logs

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

---

## Production Deployment Options

### Option 1: Cloud Platform (Recommended)

#### AWS Deployment

**Services Used:**
- **ECS/Fargate**: Container orchestration
- **RDS PostgreSQL**: Managed database
- **ElastiCache Redis**: Managed cache
- **S3**: Static file storage
- **CloudFront**: CDN for frontend
- **ALB**: Load balancer

**Steps:**
1. Create RDS PostgreSQL instance
2. Create ElastiCache Redis cluster
3. Build and push Docker images to ECR
4. Create ECS task definitions
5. Deploy services to ECS
6. Configure ALB with health checks
7. Set up CloudFront for Next.js frontend

#### Google Cloud Platform

**Services Used:**
- **Cloud Run**: Serverless containers
- **Cloud SQL**: PostgreSQL
- **Memorystore**: Redis
- **Cloud Storage**: Static files
- **Cloud CDN**: Content delivery

#### Azure

**Services Used:**
- **Container Instances**: Docker containers
- **Azure Database for PostgreSQL**
- **Azure Cache for Redis**
- **Azure Storage**
- **Azure CDN**

---

### Option 2: VPS Deployment

For a single VPS (DigitalOcean, Linode, etc.):

**Requirements:**
- Ubuntu 22.04 LTS
- 4GB RAM minimum
- 2 CPU cores
- 40GB storage

**Setup Steps:**

1. **Install Docker and Docker Compose**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y

# Add user to docker group
sudo usermod -aG docker $USER
```

2. **Clone Repository**
```bash
git clone https://github.com/your-org/AQRFactorX.git
cd AQRFactorX
```

3. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with production values
nano .env
```

4. **Set Up SSL with Let's Encrypt**
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com -d api.yourdomain.com
```

5. **Configure Nginx Reverse Proxy**
```bash
sudo nano /etc/nginx/sites-available/aqr-factor-explorer
```

Add configuration:
```nginx
# Frontend
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

6. **Enable Site and Reload Nginx**
```bash
sudo ln -s /etc/nginx/sites-available/aqr-factor-explorer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

7. **Start Application**
```bash
docker-compose up -d
```

8. **Load Data**
```bash
# Copy AQR data files to data/aqr_raw/
# Then run ingestion
docker-compose exec backend python -m backend.etl.ingest_aqr_factors --data-dir /data/aqr_raw
```

---

## Environment Variables

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://user:password@postgres:5432/aqr_factors

# Redis
REDIS_URL=redis://redis:6379/0

# API
PORT=8000
API_CORS_ORIGINS=https://yourdomain.com

# Logging
LOG_LEVEL=INFO

# Security (add for production)
SECRET_KEY=your-secret-key-here
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NODE_ENV=production
```

---

## Database Migrations

### Running Migrations

```bash
# In Docker
docker-compose exec backend alembic upgrade head

# Or locally
cd backend
alembic upgrade head
```

### Creating New Migrations

```bash
# Auto-generate migration
make migrate-create MESSAGE="description of changes"

# Or manually
docker-compose exec backend alembic revision --autogenerate -m "description"
```

---

## Monitoring & Logging

### Health Checks

```bash
# Check all services
curl https://api.yourdomain.com/api/monitoring/health/detailed

# System stats
curl https://api.yourdomain.com/api/monitoring/stats
```

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Set Up Log Aggregation

For production, use:
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Grafana Loki**
- **Cloud provider logging** (CloudWatch, Stackdriver, etc.)

---

## Backup Strategy

### Database Backups

**Automated Daily Backups:**
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U aqr_user aqr_factors > backup_$DATE.sql
gzip backup_$DATE.sql
# Upload to S3 or backup storage
aws s3 cp backup_$DATE.sql.gz s3://your-bucket/backups/
```

Add to crontab:
```bash
0 2 * * * /path/to/backup.sh
```

### Restore from Backup

```bash
gunzip backup_20240115.sql.gz
docker-compose exec -T postgres psql -U aqr_user aqr_factors < backup_20240115.sql
```

---

## Scaling

### Horizontal Scaling

1. **Database**: Use read replicas
2. **API**: Run multiple backend containers behind load balancer
3. **Cache**: Use Redis Cluster
4. **Frontend**: Deploy to CDN (Vercel, Netlify, CloudFront)

### Vertical Scaling

Increase Docker container resources:

```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

---

## Security Checklist

- [ ] Use strong database passwords
- [ ] Enable SSL/TLS for all connections
- [ ] Set up firewall rules
- [ ] Implement rate limiting
- [ ] Enable CORS only for trusted domains
- [ ] Regular security updates
- [ ] Database connection encryption
- [ ] Secrets management (AWS Secrets Manager, Vault, etc.)
- [ ] API authentication (if needed)
- [ ] Regular backups
- [ ] Monitoring and alerting

---

## Performance Optimization

### Database

```sql
-- Create indexes for common queries
CREATE INDEX CONCURRENTLY idx_factor_return_date_range
ON factor_return (factor_id, date);

-- Analyze tables regularly
ANALYZE factor;
ANALYZE factor_return;

-- Vacuum regularly
VACUUM ANALYZE;
```

### Redis Caching

- Cache expensive queries (1 hour TTL)
- Cache static data (24 hour TTL)
- Implement cache warming on startup

### Frontend

- Enable Next.js static generation
- Use CDN for static assets
- Implement image optimization
- Enable compression

---

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U aqr_user -d aqr_factors -c "SELECT 1"
```

### Redis Connection Issues

```bash
# Check Redis
docker-compose exec redis redis-cli ping

# Should return: PONG
```

### High Memory Usage

```bash
# Check container stats
docker stats

# Restart services
docker-compose restart
```

---

## Maintenance

### Regular Tasks

**Daily:**
- Check logs for errors
- Monitor disk space
- Verify backups completed

**Weekly:**
- Review performance metrics
- Update AQR data
- Check for security updates

**Monthly:**
- Review and optimize database
- Update dependencies
- Review access logs

---

## Updating the Application

```bash
# Pull latest code
git pull

# Rebuild containers
docker-compose build

# Restart with new images
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head
```

---

## Support & Resources

- **Documentation**: See README.md and API.md
- **Health Check**: `/api/monitoring/health/detailed`
- **API Docs**: `/api/docs`
- **Logs**: `docker-compose logs -f`

---

**Need help?** Open an issue on GitHub or check the troubleshooting section above.
