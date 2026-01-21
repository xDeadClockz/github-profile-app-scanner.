Project name: “github-profile-app-scanner”Description: Python CLI that lists applications connected to a GitHub account and highlights potentially risky ones.
Requirements:Python 3.10+GitHub PAT with read:user (and optional extra scopes if needed). 
Install:git clone <repo>pip install -r requirements.txt
Usage:python -m github_app_scanner --token <GITHUB_TOKEN>

# GitHub Profile App Scanner

Simple Python CLI tool that lists GitHub App installations accessible to a GitHub personal access token and runs basic heuristic checks.

## Requirements

- Python 3.10+
- A GitHub Personal Access Token (classic or fine-grained) with at least `read:user`.  
  Generate one from GitHub Settings → Developer settings → Personal access tokens. [web:24]

## Install

```bash
git clone https://github.com/<your-username>/github-profile-app-scanner.git
cd github-profile-app-scanner
pip install -r requirements.txt
# or: pip install .
