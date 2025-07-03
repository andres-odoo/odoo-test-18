# odoo-test-16 Docker Environment Documentation

Welcome to odoo-test!

This documentation provides a step-by-step guide to set up and use the dockerized environment for the `odoo-test`. Let's get started!

## Branch Naming and Commit Messages

To keep things organized and easy to track, we follow specific conventions for branch names and commit messages.

### Branch Naming Convention

When creating new branches, please use one of the following prefixes:

- `migration/` for migration tasks
- `feature/` for new features
- `hotfix/` for critical fixes
- `fix/` for general bug fixes

After the prefix, add the ticket name in the format `{PROJECT_CODE}-123`, followed by an underscore and the branch name. For example: `feature/TEST-123_new_branch`.

### Commit Message Convention

For each commit, use the following structure for your commit message:

```text
{PROJECT_CODE}-123: Your commit message
```

For example: `TEST-123: Add new module`.

## 🚀 Development Guidelines

At odoo-test-16, we believe in delivering high-quality code that not only works flawlessly but also adheres to industry-standard best practices. To achieve this,

1. We need to have the knowledge for all [odoo ORM](https://www.odoo.com/documentation/16.0/developer/reference/backend/orm.html)
2. We align with the [Odoo guidelines](https://www.odoo.com/documentation/16.0/contributing/development/coding_guidelines.html)

3. We align with the Odoo Community Association (OCA) guidelines. These guidelines serve as a cornerstone for ensuring exceptional code quality and uniformity throughout the Odoo community. You can find the comprehensive [OCA Guidelines here](https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst).

4. We have incorporated a comprehensive set of development guidelines and code quality tools. Let's explore them:

### 💡 Code Quality Tools

We utilize a combination of powerful code quality tools to maintain top-notch code standards and consistency:

1. **darker**

   - Repository: [https://github.com/akaihola/darker](https://github.com/akaihola/darker)
   - Description: Darker automatically reformats Python code to adhere to the latest PEP 8 guidelines, providing a consistent and clean codebase.
   - Importance: Ensures uniform code style and consistency, improving readability and maintainability.

2. **autopep8**

   - Repository: [https://github.com/pre-commit/mirrors-autopep8](https://github.com/pre-commit/mirrors-autopep8)
   - Description: Autopep8 automatically formats Python code according to the PEP 8 guidelines, fixing style issues like indentation, line length, and whitespace.
   - Importance: Enhances code readability and ensures codebase compliance with PEP 8 guidelines.

3. **pre-commit-hooks**

   - Repository: [https://github.com/pre-commit/pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks)
   - Hooks: check-toml, check-yaml, end-of-file-fixer, trailing-whitespace
   - Description: This section contains several useful pre-commit hooks provided by pre-commit-hooks. They check and fix issues like TOML and YAML formatting, trailing whitespace, and missing end-of-file newline.
   - Importance: Enforces consistent code formatting and eliminates common mistakes.

4. **prettier**

   - Repository: [https://github.com/pre-commit/mirrors-prettier](https://github.com/pre-commit/mirrors-prettier)
   - Description: Prettier is a versatile code formatter for JavaScript and CSS files, ensuring code consistency and readability.
   - Importance: Improves code style and consistency for JavaScript and CSS files.

5. **ruff**

   - Repository: [https://github.com/charliermarsh/ruff-pre-commit](https://github.com/charliermarsh/ruff-pre-commit)
   - Description: Ruff is a static code analyzer for Python, which checks for common programming errors and enforces PEP 8 guidelines.
   - Importance: Helps detect and fix errors in Python code, enhancing code quality.

6. **pylint**
   - Repository: [https://github.com/PyCQA/pylint](https://github.com/PyCQA/pylint)
   - Description: Pylint is a powerful static code analysis tool for Python. It enforces coding standards, detects errors, and ensures code consistency.
   - Importance: Pylint is crucial for maintaining high-quality Python code, identifying potential issues, and enforcing best practices.

By embracing these cutting-edge code quality tools and following the industry-standard development guidelines, we ensure that our codebase remains robust, efficient, and maintainable. Each tool serves a vital role in enhancing code quality, readability, and overall development efficiency. Let's code with passion and excellence! 😁🔥

## Initial Setup

Before diving into the exciting development work, let's set up the environment!

1. **Login to the `gitlab.syscoon.com` Docker registry**:

   Before proceeding, make sure you have valid credentials for the `gitlab.syscoon.com` Docker registry. Use the following command to log in:

   ```bash
   docker login gitlab.syscoon.com:5050 -u <username> -p <token>
   ```

2. **Prepare the Local Environment**:

   Run the setup script in your terminal:

   ```bash
   ./config/setup.sh <ODOO_VERSION> <DEBUG_SETUP(0|1)>
   ```

   This script will create a `.env` file with the necessary variable configurations. The arguments to pass are as follows:

   - `<ODOO_VERSION>`: Choose from `18.0`, `17.0`, `16.0`, `15.0`, `14.0`, or `13.0`.
   - `<DEBUG_SETUP>`: Set to `1` for debugging setup, `0` for regular setup.

   For example, to set up with Odoo version `18.0` and enable debugging, run:

   ```bash
   ./config/setup.sh 18.0 1
   ```

   The `.env` file will be created with the necessary configurations.

3. **Configure and Run ODOO**:

   In the `docker-compose.yml` file, you can customize ODOO settings such as debug mode and database configurations.

   - If you are using `vscode`, set `CLIENT_WAIT=True` to run Odoo only when the debug server is running.
   - Use `DEBUG_INIT_DB` to specify a specific database at startup.
   - Use `DEBUG_INIT_MODULES` to install specific modules for the created database.
   - Use `DEBUG_INIT_PATH` to install all modules found in a specific path for the created database.

   To start ODOO, run:

   ```bash
   docker-compose up --build
   ```

Setting up Visual Studio Code (vscode)
Proper configuration in vscode is crucial for effective development and debugging. Follow these steps:

1. **Organize Workspace Folders**:

   Ensure your workspace folders are set up as follows:

   ```text
   - root_folder
      - odoo # baseOdoo folder
      - enterprise # enterpriseAddons
      - design-themes # odooBaseAddons for themes
      - projects # all running projects
         - odoo-ci
         - odoo-test-16
         - syscoon-odoo-server
         - ...
   ```

2. **Sync Odoo Addons Folders**:

   For debugging in vscode, the `odoo/addons` and `odoo/odoo/addons` folders are synced into one folder. The setup script handles this automatically.

3. **Configure `launch.json`**:

   In the `.vscode` folder, update the `launch.json` file with the following configurations:

   ```json
   {
     "name": "16: TEMP",
     "type": "python",
     "request": "attach",
     "port": 8069,
     "debugServer": 3001,
     "host": "localhost",
     "pathMappings": [
       {
         "localRoot": "${workspaceFolder}/projects/odoo-test-16/internal_addons",
         "remoteRoot": "/mnt/odoo/internal_addons"
       },
       {
         "localRoot": "${workspaceFolder}/projects/odoo-test-16/external_addons",
         "remoteRoot": "/mnt/odoo/external_addons"
       },
       {
         "localRoot": "${workspaceFolder}/odoo-sync/addons",
         "remoteRoot": "/usr/lib/python3/dist-packages/odoo/addons"
       },
       {
         "localRoot": "${workspaceFolder}/enterprise",
         "remoteRoot": "/mnt/odoo-enterprise"
       },
       {
         "localRoot": "${workspaceFolder}/design-themes",
         "remoteRoot": "/mnt/design-themes"
       }
     ],
     "logToFile": true,
     "justMyCode": false
   }
   ```

   With these configurations, you can easily add breakpoints and debug your code effectively in vscode.

Windows Users
As a Windows user, the setup process using `./config/setup.sh` is not available yet. However, don't worry! You can still set up the project manually by following these instructions:

1. **Create a `.env` File**:

   Create a new file in the project folder and name it `.env`. Then, add the following data to the file:

   ```text
   PROJECT_CODE=TEST
   ODOO_PORT=8069:8069
   POSTGRES_DB=postgres
   POSTGRES_PASSWORD=odoo
   POSTGRES_USER=odoo
   PGADMIN_DEFAULT_EMAIL=local@local.com
   PGADMIN_DEFAULT_PASSWORD=1234
   DEBUG_PORT=3001
   ```

   Save the file after adding the above configurations.

2. **Install `pre-commit`**:

   Open your terminal or command prompt and run the following commands to install `pre-commit` and `python-dotenv` to your project:

   ```bash
   pip install pre-commit python-dotenv
   pre-commit install
   ```

   This will set up the necessary hooks for code quality checks.

3. **Copy Git Hooks**:

   Locate the following files in the project:

   - `./config/scripts/commit_msg.py`
   - `./config/scripts/pre_push.py`

   Copy these files into the `.git/hooks` directory.

   Now, you are all set to start coding! Happy coding and have a productive development experience with `odoo-test-16`!
