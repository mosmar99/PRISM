# PRISM (Pharmaceutical Risk Interaction and Safety Monitor)

![image](https://github.com/user-attachments/assets/2a16d1a7-c339-482b-8334-cb55fef1ab3b)

## Table of Contents

- [Prerequisites](#Prerequisites)
- [Usage](#Usage)
- [Authors](#Authors)



### Prerequisites

Make sure you have Python and pip installed on your machine.

1.  **Install Python**
    
    *   **Windows**: Download the installer from the [official Python website](https://www.python.org/downloads/windows/) and run it. Make sure to check the box that says "Add Python to PATH" during installation.
    *   **macOS**: You can use Homebrew to install Python. Open your terminal and run:
        
        ```bash
        brew install python
        python -m ensurepip --upgrade
        ```
    *   **Linux**: Use your package manager to install Python. For example, on Ubuntu, run:
        
        ```bash
        sudo apt update
        sudo apt install python3 python3-pip
        ```
        
2.  **Verify the installation**
    
    After installation, verify that Python and pip are installed correctly by running the following commands in your terminal or command prompt:
    
    ```bash
    python --version
    pip --version
    ```
    
3.  **Clone the repository**
    
    ```bash
    git clone https://github.com/mosmar99/PRISM.git
    cd PRISM
    ```

4.  **Create a virtual environment (optional but recommended)**
    
    ```bash
    python -m venv venv
    # Activate the virtual environment
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```
    
5.  **Install dependencies**
    
    ```bash
    pip install -r requirements.txt
    ```

    ```bash
    # if this doesn't work try restarting your terminal
    chainlit --version
    ```

    **Connecting to the Gemini API**

    Google's gemini model has a free API version info here:

    https://ai.google.dev/pricing#1_5flash
    
    Get your Google API key here:

    https://aistudio.google.com/app/apikey

    Whilst in the PRISM directory type:
    ```bash
    # Using windows powershell.
    New-Item .env
    # linux / macos
    touch .env
    ```

    open up your newly create .env file, and add the following line
    ```bash
    # replace the text within the quotation marks ("") with your actual API key, make sure you keep the quotation marks
    API_KEY = "YOUR_API_KEY_GOTTEN_FROM_GOOGLE"
    ```


### Usage
After verifying your installations as descibed above, getting your API key & creating your .env file run the application as such:
```bash
chainlit run .\src\main.py
```
This will open up a web application on the local network at port 8000.
After the application has started you may select your chat profile at the drop down menu at the top!

If the above command doesn't work you can verify your chainlit installation by:
```bash
chainlit run hello
```
If that works something is probably wrong with your API key / .env file.

### Authors

- **Mahmut Osmanovic (mosmar99)**
- **Isac Paulsson (isacpaulsson)**
- **Sebastian Tuura (tuura01)**
- **Clément Pickel (clementpickel)**
- **Célian Freidrich (friedrichcelian)**