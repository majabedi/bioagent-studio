# Streamlit Deployment Guide

This guide explains how to deploy the Biological ABM Assistant as a Streamlit application.

## 1. Prepare the application

1. Activate the virtual environment:

```bash
cd /home/majid/Desktop/bioagent-studio
. .venv/bin/activate
```

2. Install or update dependencies:

```bash
pip install -r requirements.txt
```

3. Copy the example environment file:

```bash
cp .env.example .env
```

4. Edit `.env` and set the required values:

- `LLM_API_KEY`
- `LLM_BASE_URL`
- `LLM_MODEL`

Optional values can also be adjusted to control timeout, temperature, and simulation limits.

## 2. Run locally with Streamlit

Start the app locally for verification:

```bash
streamlit run app.py
```

Then open the displayed local URL in your browser.

## 3. Deploy to a cloud host

This repository includes Streamlit-ready configuration files:
- `.streamlit/config.toml`: Streamlit theme and client settings (committed to version control).
- `.streamlit/secrets.toml.example`: Example secrets file (committed; use as a template).
- `.streamlit/secrets.toml`: Local secrets (add to `.gitignore`; create locally or via Streamlit Cloud UI).

Use any Streamlit-compatible host or container platform. The following options are common:

### Option A: Streamlit Community Cloud (Recommended)

**Step 1: Prepare your GitHub repository**

1. Ensure all changes are committed and pushed to GitHub:
   ```bash
   git add .
   git commit -m "Add Streamlit Cloud configuration"
   git push origin main
   ```

2. Create a `.gitignore` entry (if not present) to exclude secrets:
   ```
   .streamlit/secrets.toml
   .env
   .env.local
   ```

**Step 2: Deploy to Streamlit Community Cloud**

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. Click **"New app"** and select:
   - Repository: `your-username/bioagent-studio` (or your fork)
   - Branch: `main`
   - Main file path: `app.py`
3. Click **"Deploy"**. Streamlit will build and start the app in a few minutes.

**Step 3: Add secrets to Streamlit Cloud**

1. After deployment, click the **"hamburger menu"** (≡) → **"Settings"**.
2. Go to the **"Secrets"** tab.
3. Paste your secrets in TOML format:
   ```toml
   LLM_API_KEY = "your-api-key-here"
   LLM_BASE_URL = "https://your-openai-compatible-endpoint.example/v1"
   LLM_MODEL = "your-model-name"
   ```
4. Click **"Save"**. The app will automatically restart with the secrets loaded.

**Automatic updates:** Push changes to the GitHub repo, and Streamlit Cloud will automatically redeploy within ~1 minute.

### Option B: Docker container

1. Create a Dockerfile for the app.
2. Build the image:

```bash
docker build -t bioagent-abm-assistant .
```

3. Run the container with environment variables:

```bash
docker run -p 8501:8501 \
  -e LLM_API_KEY="your-key" \
  -e LLM_BASE_URL="https://your-openai-compatible-endpoint.example/v1" \
  -e LLM_MODEL="your-model-name" \
  bioagent-abm-assistant
```

### Option C: Other cloud providers

You can deploy on services such as Heroku, AWS Elastic Beanstalk, Google Cloud Run, or Azure Web Apps. Use the same application command:

```bash
streamlit run app.py
```

If your platform reports a missing top-level `app`, `application`, or `handler` variable, it is detecting the project as a generic Python web app instead of a Streamlit app. In that case:

- Use a Streamlit-specific host such as Streamlit Community Cloud, or
- Add a `Procfile` or deployment command that runs `streamlit run app.py`.

This repository now includes a `Procfile` to support platforms that respect process definitions.

## 4. Important deployment considerations

- Do not commit `.env` or secrets to source control.
- Keep `LLM_API_KEY` private.
- Use environment variables for all external configuration.
- Monitor API usage and costs when the app calls the LLM.
- The app is intended for small, exploratory simulations, not large-scale production workloads.

## 5. Troubleshooting

- If the app fails to start, verify environment variables are set.
- Confirm that `streamlit` is installed in the active environment.
- If the LLM endpoint is unreachable, check the URL and network access.
- If simulation limits are exceeded, lower the initial agent counts or steps.

## 6. Next steps after deployment

- Add secure secret management for deployment.
- Add logging and monitoring for LLM requests.
- Consider rate limiting and authentication for public deployments.
