import sys
import os
import time
from dotenv import load_dotenv

# Load environment variables once at the start
load_dotenv()

# Import the modules. 
# Note: Since app.py and mail.py have their logic inside main() functions 
# guarded by if __name__ == "__main__", importing them won't run the code immediately.
import app
from Mail_SMTP import mail

def header(text):
    print("\n" + "="*60)
    print(f">>> {text}")
    print("="*60 + "\n")

def main():
    print(">>> STARTING NEWS AUTOMATION PIPELINE (Integrated Mode) <<<\n")

    # Step 1: Run the App (Fetch -> Process -> Summarize -> Save JSON)
    header("STEP 1: Fetching & Summarizing News")
    try:
        app.main()
        print("\n[SUCCESS] News processing completed.")
    except Exception as e:
        print(f"\n[ERROR] Failed during news processing: {e}")
        sys.exit(1)

    # Step 2: Run the Mailer (Read JSON -> Format -> Send Email)
    header("STEP 2: Sending Email")
    try:
        mail.main()
        print("\n[SUCCESS] Email sequence completed.")
    except Exception as e:
        print(f"\n[ERROR] Failed during email sending: {e}")
        sys.exit(1)

    header("PIPELINE COMPLETED SUCCESSFULLY")

if __name__ == "__main__":
    main()
