# notes-to-text
Converting handwritten notes to digital text


## Project Setup

```
git clone https://github.com/vee-16/notes-to-text.git
cd notes-to-text
cp .env.example .env
python3 -m venv ocr
source ocr/bin/activate
pip install -r requirements.txt
```

## API Setup

> Note: Do not commit `.env` and keys.

1. Goodle Cloud Document AI
- Create a GCP Project
- Enable Document AI API
- Create a Processor
- Create Service Account & Key

```
mv ~/Downloads/YOUR_KEY.json keys/docai_key.json
```

- Add to `.env`

```
GOOGLE_APPLICATION_CREDENTIALS=keys/docai_key.json
GCP_PROJECT_ID=YOUR_PROJECT_ID
GCP_LOCATION=us
GCP_PROCESSOR_ID=YOUR_PROCESSOR_ID
```

2. OpenAI 
- Generate an OPEN AI API key from https://platform.openai.com/api-keys 

- Add the key to `.env`: OPENAI_API_KEY=your-key
