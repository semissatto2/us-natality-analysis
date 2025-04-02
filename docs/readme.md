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

