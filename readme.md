# US Natality Data Pipeline & Dashboard
![Pipeline Diagram](/images/us-natality-pipeline.png)

## 📌 Project Overview
This project is part of my final project for the [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp).

This project analyzes US natality data from 1969 to 2008, containing over 20GB of data available via Google Public Datasets. The goal is to build a cloud-based data pipeline that ingests, processes, and visualizes key birth trends through an interactive dashboard.

### 🔍 Key Business Questions
The dashboard provides insights into:
1. **Gender distribution of newborns** (Male vs. Female).
2. **Yearly birth trends** across the United States.
3. **Total births by state** and their percentage share.
4. **Monthly birth distribution** to observe seasonal patterns.
5. **Gestation period distribution** (percentage of births per gestation week).
6. **Correlation between birth weight and gestation period.**

## 🏗️ Project Architecture
The project is fully implemented in Google Cloud, leveraging Terraform for Infrastructure as Code (IaC), Apache Airflow for orchestration, PySpark for data processing, and Looker Studio for visualization.

### ⚙️ Tech Stack
- **Cloud Provider**: Google Cloud Platform (GCP)
- **Infrastructure as Code**: Terraform
- **Orchestration**: Apache Airflow
- **Compute**: Google Compute Engine (VMs), Google Dataproc (Spark Cluster)
- **Storage**: Google Cloud Storage (GCS)
- **Data Warehouse**: BigQuery
- **Processing Framework**: PySpark
- **Visualization**: Looker Studio

### 🔗 Data Flow
1. **Google Cloud Setup**: A new GCP project is created, and credentials are generated.
2. **Infrastructure Deployment**: Using Terraform, the following resources are provisioned:
   - Virtual Machine (Compute Engine)
   - Cloud Storage Bucket (GCS)
   - BigQuery Dataset
3. **Data Pipeline Execution (Apache Airflow)**:
   - **Download natality data** from Google Public Datasets.
   - **Upload raw data** to Google Cloud Storage (GCS).
   - **Launch a Dataproc cluster** to process the data with PySpark.
   - **Transform and load** data into BigQuery for analysis.
   - **Terminate Dataproc cluster** after processing to optimize costs.
4. **Dashboard Development**:
   - Data is retrieved from BigQuery into Looker Studio.
   - The dashboard is built with visualizations answering the key business questions.

## 📊 Data Visualization
The final dashboard consists of multiple charts providing deep insights into birth trends in the US.

| Chart | Description |
|--------|------------|
| **1. Gender Distribution** | Proportion of male vs. female births. |
| **2. Yearly Birth Trends** | Time series showing birth trends across years. |
| **3. Births by State** | Total births per state and their percentage share. |
| **4. Births by Month** | Monthly distribution of births. |
| **5. Gestation Period Distribution** | Percentage of births per gestation week. |
| **6. Birth Weight vs. Gestation** | Correlation between baby weight and gestation period. |

## 🖼️ Project Diagrams
### **1. Data Pipeline Architecture**
![Pipeline Diagram](/images/us-natality-pipeline.png)

### **2. Airflow DAG (Workflow Orchestration)**
![Airflow DAG](/images/airflow_pipeline.PNG)

### **3. Dashboard Sample**
![Dashboard Part 1](/images/dashboard_view_1.PNG)
![Dashboard Part 2](/images/dashboard_view_2.PNG)

## 📌 Reproducibility

This section provides a detailed step-by-step guide on how to set up and run the project from scratch in the Google Cloud environment.

### 1️⃣ Create Google Cloud Project and Service Account (SA)

#### Create a GCP Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Create Project**
3. Set the project name as `us-natality`
4. A unique project ID will be generated, e.g., `us-natality-XXXX`
5. In this example, the project ID is `us-natality-455214`

#### Create a Service Account (SA)
1. Navigate to **IAM & Admin** → **Service Accounts**
2. Click **Create Service Account**
3. Set the name and role as **Owner**

#### Generate and Download Credentials
1. In the **Service Accounts** page, check the created SA
2. Click on the three-dot menu (**⋮**) → **Manage Keys** → **Create New Key**
3. Select **JSON** and download the file
4. Move the file to the project root and rename it as `credentials.json`
5. The service account email will be something like:
   ```bash
   us-natality-sa@us-natality-455214.iam.gserviceaccount.com
   ```

### 2️⃣ Enable Required APIs and Permissions

#### Enable VM API
1. Navigate to **Compute Engine** → **VM Instances**
2. Click **Enable**

#### Enable Cloud Resource Manager API
1. Go to **API & Services** → **Cloud Resource Manager API**
2. Click **Enable**

#### Grant Permissions to the Service Account
1. Navigate to **IAM & Admin** → **IAM**
2. Click **Grant Access**
3. Add the Service Account email and assign the **Owner** role

#### Enable Dataproc API and Permissions
1. Navigate to **GCP Console** → **Storage**
2. Search for **Dataproc API** → **Enable APIs**
3. Go to **IAM & Admin** → **IAM**
4. Click on the created Service Account
5. Click **Grant Access** → **Add Role** → **Dataproc Administrator**

### 3️⃣ Deploy Infrastructure with Terraform

#### Update Terraform Variables
1. Open the `variables.tf` file
2. Replace values labeled as `TODO` with actual project details

#### Run Terraform Commands
```bash
tf init
tf plan
tf apply
```
To destroy resources:
```bash
tf destroy
```

### 4️⃣ Create SSH Key and Connect to VM

#### Generate SSH Key
```bash
mkdir -p ~/.ssh
ssh-keygen -t rsa -b 2048 -f ~/.ssh/id_rsa -C "your-email@example.com"
```
This generates two files: `id_rsa` (private key) and `id_rsa.pub` (public key).

#### Add SSH Key to VM
1. Navigate to **Compute Engine** → **VM Instances**
2. Go to **Settings** → **Metadata** → **SSH Keys**
3. Copy and paste the content of `id_rsa.pub`

#### Connect to VM
```bash
ssh -i ~/.ssh/id_rsa username@YOUR_VM_EXTERNAL_IP
```

### 5️⃣ Setup VM Environment

#### Update and Install Docker
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
docker --version
```

#### Install Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

#### Configure GCP Credentials on VM
```bash
mkdir -p ~/.google/credentials
scp -i ~/.ssh/id_rsa credentials.json username@YOUR_VM_EXTERNAL_IP:~/.google/credentials/google_credentials.json
```

### 6️⃣ Setup and Run Airflow

#### Clone Repository and Configure
```bash
git clone YOUR_REPO_URL
cd YOUR_REPO_DIR
```
Edit the necessary Airflow configuration files (`TODO` placeholders) with project details.

#### Start Airflow
```bash
docker-compose up --build
```
Wait until all services are up and running.

#### Access Airflow Web UI
1. Forward port `8080` to your local machine
2. Open [localhost:8080](http://localhost:8080)
3. Login with:
   - **Username**: `airflow`
   - **Password**: `airflow`

#### Activate and Run DAG
1. Go to **DAGs**
2. Activate `natality_web_data_to_gcs`
3. Click **Trigger DAG** (▶️)

#### Validate Data Upload to GCS
- The pipeline should generate 12 files (~400MB each) in the specified GCS bucket.
- If the **Dataproc Operator** fails due to permission errors:
  1. Navigate to **IAM & Admin** → **IAM**
  2. Find the newly created SA and add **Storage Admin** role

#### Edit PySpark Script
- Once the Dataproc cluster is created, find the **Dataproc Temp Bucket** and update it in the PySpark script (`dags/pyspark_script.py`).

### 7️⃣ Expected Runtime
The full pipeline takes **~27 minutes** to complete, depending on network speed.


## 📌 Next Steps
- Fine-tune Airflow DAG to optimize scheduling and execution times.
- Create shell scripts to make reprodutibility easier

---

This project showcases end-to-end data engineering practices, leveraging cloud technologies and best practices for scalable data pipelines. 🚀

