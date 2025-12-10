# notes-to-text
Converting handwritten notes to digital text


## Project Setup

```bash
git clone https://github.com/vee-16/notes-to-text.git
cd notes-to-text
cp .env.example .env
python3 -m venv ocr
source ocr/bin/activate
pip install -r requirements.txt
```

## API Setup

> Note: Do not commit `.env` and keys.

#### 1. Goodle Cloud Document AI
- Create a GCP Project: https://console.cloud.google.com/projectcreate
    - Copy the Project Number
- Enable Document AI API for project: https://console.cloud.google.com/apis/library/documentai.googleapis.com
- Create a Document OCR Processor with Region as US: https://console.cloud.google.com/ai/document-ai/processor-library
    - Copy the Processor ID
- Create Service Account & Key: https://console.cloud.google.com/iam-admin/serviceaccounts/create
    - Grant the following Permission roles: 
        - Document AI API User (Beta)
        - Document AI Editor (Beta)
    - After creating the service account, under actions, select `Manage Keys` > `Add a key` > and create a new json key
        - Move the downloaded key under the project's directory using: 
        ```bash
        mv ~/Downloads/YOUR_KEY.json keys/docai_key.json
        ```

- Add to `.env`

```Dotenv
GOOGLE_APPLICATION_CREDENTIALS=keys/docai_key.json
GCP_PROJECT_ID=your-project-id
GCP_LOCATION=us
GCP_PROCESSOR_ID=your-processor-id
```

####  2. OpenAI 
- Generate an OPEN AI API key from https://platform.openai.com/api-keys 

- Add the key to `.env`: 

```Dotenv
OPENAI_API_KEY=your-key
```


#### Strip Notebook Outputs:
Notebook outputs are automatically stripped on every commit using a git hook (via [nbstripout](https://github.com/kynan/nbstripout)) to avoid leaking private data.

You can also strip outputs manually at any time by running `nbstripout notebooks/<your-noteboook>.ipynb` before commiting your changes.
