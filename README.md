# Project Setup & Installation Guide

This repository contains the setup instructions for running the facial recognition project across **Windows**, **macOS**, and **Linux**.

---

##  -> Architecture Reference

For a complete walkthrough of the project's architecture, check out the video reference below:
* **Video Reference:** [Architecture Overview on YouTube](https://www.youtube.com/watch?v=oHSesteFK5c)

---

## -> Prerequisites

Make sure Python 3 is installed on your system. You can verify your installation by running:

* **Windows:**
  ```cmd
  py --version
  ```
* **macOS / Linux:**
  ```bash
  python3 --version
  ```

---

## -> Installation Steps


### Step 1: Create & Activate Virtual Environment

Isolate your project dependencies from your system-wide Python environment.

#### Windows (Command Prompt / PowerShell):
```cmd
py -m venv venv
```
```cmd
venv\Scripts\activate
```
#### macOS / Linux:
```bash
python3 -m venv venv
```
```bash
source venv/bin/activate
```

*(Once activated, you can run `pip` directly without needing `py` or `python3` prefixes.)*

---

### Step 2: Upgrade `pip`

With the virtual environment **activated**, update its `pip` to the latest version to prevent installation issues with wheel packages (such as `opencv-python`).

* **All OS (virtual environment active):**
  ```bash
  python -m pip install --upgrade pip
  ```

* **Verify the version:**
  ```bash
  pip --version
  ```

---

### Step 3: Install Required Packages

#### Option A: Install via `requirements.txt` (Recommended)

With the virtual environment active (All OS):
```bash
pip install -r requirements.txt
```

---

#### Option B: Install Packages Individually

If you prefer to install packages manually, with the virtual environment active (All OS):
```bash
pip install boto3
pip install opencv-python
pip install pillow-heif
```

---

## -> Included Dependencies

| Package | Description |
| :--- | :--- |
| `boto3` | AWS SDK for Python |
| `opencv-python` | Computer vision and image processing library |
| `pillow-heif` | HEIF/HEIC image format support for Pillow |