# Chuyển vào đúng thư mục airflow
cd "C:\Users\acer\Desktop\Projects\crawl-topcv-jobs\airflow"

# Stopping and removing all containers, networks, and volumes...
docker-compose down -v

# If we want to keep volumes: docker-compose down

# Building new Docker image...
# docker-compose build --no-cache

# Initializing Airflow database and admin user...
docker-compose up airflow-init

# Starting all Airflow services in detached mode...
docker-compose up -d

# Done! Airflow should be running with the latest code and dependencies.