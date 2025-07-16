# robot
# 🤖 Robot: The Ultimate File & Project Scaffolding Wizard

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/new-beginne/robot/blob/main/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://github.com/new-beginne/robot/pulls)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

An intelligent, reversible file operator and project scaffolding tool with a built-in, user-friendly wizard. Stop creating project structures manually and let the robot do the heavy lifting for you!

 
> **Note:** It's highly recommended to record a short GIF of the wizard in action and replace the link above. You can use tools like [ScreenToGif](https://www.screentogif.com/) or [Peek](https://github.com/phw/peek).

---

## ✨ Why This Robot?

Setting up a new project involves creating a repetitive structure of folders and files. This manual process is tedious, slow, and prone to errors. This robot solves this problem by providing a powerful and forgiving command-line interface that makes project scaffolding a breeze.

## 🔥 Key Features

- **🤖 Interactive Wizard:** No need to write complex JSON. The wizard guides you step-by-step through a simple number-based menu.
- **👁️ Live Preview & Edit:** Before a single file is touched, get a beautiful tree preview of your entire planned structure.
- **💪 Powerful Review Stage:**
  - **Edit with Ease:** Rename, Delete, Copy, and Move any item directly from the preview.
  - **Forgiving Undo:** Made a mistake while editing? **Undo your last change** in the review stage with a single command.
  - **Flexible Workflow:** Forgot to add a file? No problem! **Go back to the wizard**, add more items, and then review the updated structure again.
- **⏪ 100% Reversible:** The most important feature! If anything goes wrong or you change your mind, a single `--undo` command reverts all changes, leaving your system perfectly clean.
- **📦 Zero Dependencies:** A single, self-contained Python script that runs anywhere Python is installed.

## 🚀 Getting Started

### Prerequisites
- Python 3.6 or higher.

### Installation
No installation needed! Just clone the repository and run the script.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/new-beginne/robot.git
    ```
2.  **Navigate into the directory:**
    ```bash
    cd robot
    ```

## 💻 How to Use

### 1. Wizard Mode (Default & Recommended)
This is the easiest and most powerful way to use the tool. Simply run the script (assuming you've renamed it to `robot.py`):
```bash
python3 robot.py
```
The wizard will guide you through creating your project. When you're done, you'll enter the **Review Stage**, where you can modify your structure before execution.

### 2. File Mode (For Automation)
You can also run operations directly from a pre-written JSON file. This is great for automating common project setups.

1.  Create a JSON file (e.g., `my_project.json`):
    ```json
    [
      {
        "operation": "create",
        "mode": "folder",
        "path": "my-new-app/src"
      },
      {
        "operation": "create",
        "mode": "file",
        "path": "my-new-app/src/index.js",
        "content": "console.log('Hello, World!');"
      }
    ]
    ```
2.  Run the robot with the `-i` or `--input` flag:
    ```bash
    python3 robot.py -i my_project.json
    ```

### 3. Undoing Changes
Every time you run the robot, it creates a backup of the operations. To undo the last operation, use the `--undo` flag with the **same input file** that was used to create it.

-   **To undo a wizard-generated operation:**
    ```bash
    python3 robot.py -i instructions/auto_generated.json --undo
    ```

-   **To undo an operation from a custom file:**
    ```bash
    python3 robot.py -i my_project.json --undo
    ```

## 🤝 Contributing

Contributions, issues, and feature requests are always welcome! This project was built through an iterative process, and your ideas can make it even better.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

Please feel free to check the [issues page](https://github.com/new-beginne/robot/issues) to see if you can help out.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---
*This tool was built with passion and a lot of iterations. Happy scaffolding!*
