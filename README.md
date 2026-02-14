# GCP-Recon
GCP Project Numbers Validation & Service Account Enumeration via Google API Behavior

### Details

**Summary:**  Correct guessing of  `PROJECT_ID`, extraction of the associated  `PROJECT_NUMBER`, and verification of enabled services.

> **Note:**  The critical aspect of this method is the ability to extract the  `PROJECT_NUMBER`  for any target project, even without having direct access permissions. Furthermore, it allows for validating the existence of a  `PROJECT_ID`  and identifying the specific enabled services within that project.  **Reproduction Steps:**


1.  **Generate an API Key:**  Create a token at:  [https://aistudio.google.com/api-keys](https://aistudio.google.com/api-keys)
    
2.  **Generate an Auth Token:**  Create an OAuth access token via:  [https://developers.google.com/oauthplayground/](https://developers.google.com/oauthplayground/)
    
    -   **Required Scopes (for further exploitation):**
        
        -   `https://www.googleapis.com/auth/userinfo.email`
            
        -   `https://www.googleapis.com/auth/cloud-platform`
            
        -   `https://www.googleapis.com/auth/cloud-platform.read-only`
            
        -   `https://www.googleapis.com/auth/iam`
            
        -   `https://www.googleapis.com/auth/devstorage.full_control`
            
        -   `https://www.googleapis.com/auth/compute`
            
        -   `https://www.googleapis.com/auth/sqlservice.admin`
            
        -   `https://www.googleapis.com/auth/firebase`
            
        -   `https://www.googleapis.com/auth/cloudfunctions`
            
        -   `https://www.googleapis.com/auth/gmail.readonly`
            
        -   `https://www.googleapis.com/auth/meetings.space.created`
            
        -   `https://www.googleapis.com/auth/meetings.space.settings`
            
        -   `https://www.googleapis.com/auth/devstorage.read_write`
            
        -   `https://www.googleapis.com/auth/meetings.space.readonly`
            
        -   `https://www.googleapis.com/auth/admanager`
            
        -   `https://www.googleapis.com/auth/bigquery`
            
        -   `openid`
            
        -   `https://www.googleapis.com/auth/devstorage.read_only`
            
        -   `https://www.googleapis.com/auth/bigquery.insertdata`
            
        -   `https://www.googleapis.com/auth/admin.directory.user.readonly`
            
        -   `https://www.googleapis.com/auth/compute.readonly`
            
        -   `https://www.googleapis.com/auth/userinfo.profile`
            
3.  **Configuration:**  Add your generated tokens into the following Python script:
- Change the `GEMINI_API_KEY` value to the key you created, and also swap out the `OAuth_2.0_Token` with the token you generated.
4. **Now, go ahead and run the tool:**
* **Example:**  `python PoC.py google.com:cloudsdktool bigquery-public-data`
