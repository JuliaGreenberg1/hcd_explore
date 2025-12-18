# 🧪 Researcher's Web App Starter

This is a simple, reproducible template for building internal tools using **Streamlit** and **Railway**. It's designed for researchers who want to quickly turn data scripts into interactive web applications and deploy them professionally.

---

## 🛠️ Pre-Session Setup (5 mins)

Before the session starts, please ensure you have the following:
1.  **GitHub Account** 
2.  **Railway Account:** [Sign up here](https://railway.com/new). You can log in with your GitHub account.
3.  **Python Installed:** Ensure you have Python 3.9+ on your local machine. I recommend `uv` to manage your virtual environments and python packages. 

```bash
# install uv using Homebrew
brew install uv

# shell autocomplete
# zsh
echo 'eval "$(uv generate-shell-completion zsh)"' >> ~/.zshrc

# powershell
if (!(Test-Path -Path $PROFILE)) {
  New-Item -ItemType File -Path $PROFILE -Force
}
Add-Content -Path $PROFILE -Value '(& uv generate-shell-completion powershell) | Out-String | Invoke-Expression'

```

---

## 🚀 Quick Start (Local Development)

### 1. Create your own Repository
Instead of cloning this template repo directly, use it to create your own copy on GitHub:
1.  Click the **"Use this template"** button at the top of this page.
2.  Select **"Create a new repository"**.
3.  Choose your own profile as **Owner**.
4.  Choose a name (e.g., `my-cool-app`) and click **"Create repository from template"**.

For more details, see the [GitHub documentation on creating a repository from a template](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template).

### 2. Setup Locally
```bash
# 1. Clone YOUR new repository (replace 'your-username' and 'your-repo-name')
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

# 2. Install dependencies
# Using 'uv' (recommended):
uv pip install -r requirements.txt
# OR standard pip:
# pip install -r requirements.txt
```

### 3. Configuration
- **Authentication:** 
  1. Rename `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.
  2. Open the file and set your `password`.
  3. The app will now require this password to run locally.

### 4. Develop locally
```bash
# Run the app
streamlit run app.py
```
---

## 🌐 Professional Deployment (Railway)

We use **Railway** because it provides a professional, "always-on" URL without the complexity of backend management.

### Steps to Deploy:
1.  **New Project:** In Railway, click **"New Project"** -> **"Deploy from GitHub repo"**.
2.  **Select Repo:** Choose the repository you just created from the template.
3.  **Variables (The Important Part):** 
    Railway needs to know two things to run your app professionally. Click on the app, go to the **"Variables"** tab and add:
    *   `PORT` = `8501`
    *   `password` = `your-chosen-password` (This provides the secret to the cloud app without needing a secrets.toml file)
4.  **Deploy Command:** Click on the app, go to **"Settings"** tab. Under Deploy > Custom Start Command, paste the below:
    `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
5.  **Expose your App (Get the URL):** 
    By default, Railway won't show your app to the public. To get a link:
    *   Click on the app
    *   Go to the **"Settings"** tab.
    *   Find the **"Networking"** section.
    *   Click **"Generate Domain"** (or add your own custom domain like `tools.yourlab.com`).
    *   Use port 8501 for listening, as that is what Streamlit listens on by default.
6.  **Success!** Click the new link to see your live, password-protected app.

---

## 💡 How it Works

The `app.py` file is pre-configured with:
- **Professional Look:** Hidden Streamlit branding for a "clean" feel.
- **File Uploader:** Drag and drop CSV/JSON files.
- **Interactive Filters:** Sliders and dropdowns that update charts in real-time.
- **Security:** A simple password gate for sharing with partners.

---

### ⚠️ Common Troubleshooting

**1. TabError: inconsistent use of tabs and spaces**
*   **Problem:** Python cannot mix Tabs and Spaces for indentation.
*   **The Fix:** 
    1. Open your editor (Cursor/VS Code).
    2. Press `Cmd + Shift + P` (Mac) or `Ctrl + Shift + P` (Windows).
    3. Type **"Convert Indentation to Spaces"** and hit Enter.
    4. Save, commit, and push.

**2. StreamlitSecretNotFoundError**
*   **Problem:** The app is looking for a password that hasn't been set.
*   **The Fix:** 
    *   **Locally:** Ensure `.streamlit/secrets.toml` exists.
    *   **Cloud:** Ensure you have added the `password` variable in the Railway "Variables" tab.

---

### Top 10 Streamlit Commands
1. `st.write()`: The "print" of Streamlit.
2. `st.dataframe()`: Interactive tables.
3. `st.sidebar`: Put controls on the left.
4. `st.columns()`: Create side-by-side layouts.
5. `st.file_uploader()`: Let users upload data.
6. `st.selectbox()`: Dropdown menus.
7. `st.slider()`: Numeric ranges.
8. `st.plotly_chart()`: Interactive plots.
9. `st.map()`: Geospatial visualizations.
10. `st.secrets`: Securely handle passwords/API keys.

---
Built for the *1-Hour Researcher Workshop*.
