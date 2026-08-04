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

Use any Streamlit-compatible host or container platform. The following options are common:

### Option A: Streamlit Community Cloud

- Push the repository to GitHub.
- Create a new Streamlit app and link the GitHub repo.
- Set environment variables in the Streamlit app settings.
- Use `app.py` as the main file.

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
