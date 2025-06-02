import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path
import html # For html.escape()

def send_templated_email_simplified(
    subject_line: str,
    plain_text_body: str, # Input is now plain text
    recipient_email_str: str,
    sender_email: str,
    smtp_server_address: str
):
    """
    Sends an HTML email with embedded images, using a simplified SMTP connection.
    The plain_text_body is automatically converted to basic HTML.

    Args:
        subject_line (str): The subject of the email.
        plain_text_body (str): The main content of the email as plain text.
                                Double newlines will be treated as paragraph breaks.
                                Single newlines will be treated as line breaks within a paragraph.
        recipient_email_str (str): A comma-separated string of recipient email addresses.
        sender_email (str): The email address of the sender (FROM address).
        smtp_server_address (str): The address of your SMTP server.
    """
    # ---- START OF DIAGNOSTIC PRINT STATEMENTS ----
    print("======================================================")
    print("RUNNING SCRIPT: DIAGNOSTIC VERSION - PADDING TEST 5.0") # Check for this version
    print(f"Function called for subject: {subject_line}")
    # ---- END OF DIAGNOSTIC PRINT STATEMENTS ----

    if not recipient_email_str:
        recipient_emails_list = []
    else:
        recipient_emails_list = [email.strip() for email in recipient_email_str.split(',') if email.strip()]

    if not recipient_emails_list:
        print("Error: No valid recipient emails provided in the string.")
        return

    # --- Convert plain_text_body to HTML ---
    processed_html_body = ""
    if plain_text_body and plain_text_body.strip(): # Check if there's actual content
        paragraphs_text = plain_text_body.strip().split('\n\n')
        html_paragraphs_list = []
        for para_content in paragraphs_text:
            para_content_stripped = para_content.strip()
            if para_content_stripped:
                escaped_text = html.escape(para_content_stripped)
                formatted_text = escaped_text.replace('\n', '<br>\n')
                html_paragraphs_list.append(f"<p>{formatted_text}</p>")
        
        if html_paragraphs_list:
            processed_html_body = "\n".join(html_paragraphs_list)
        else:
            processed_html_body = "<p>&nbsp;</p>"
            
    else:
        processed_html_body = "<p>&nbsp;</p>"

    # --- Create the email message ---
    msg = MIMEMultipart('related')
    msg['From'] = sender_email
    msg['To'] = ", ".join(recipient_emails_list)
    msg['Subject'] = subject_line

    try:
        script_dir = Path(__file__).resolve().parent
    except NameError:
        script_dir = Path.cwd()
        
    header_image_path = script_dir / "header.png"
    footer_image_path = script_dir / "footer.png"

    # Define the intended CSS for .content-padding
    # T:20 (top), R:40 (right), B:10 (bottom), L:40 (left)
    intended_content_padding_css = "padding: 20px 40px 10px 40px;"

    # ---- DIAGNOSTIC PRINT FOR CSS ----
    print(f"DEBUG: CSS for .content-padding will be: '{intended_content_padding_css}'")
    print("======================================================")

    email_html_structure = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{subject_line}</title>
        <style>
            body {{ font-family: Arial, Helvetica, sans-serif; background-color: #e9ecef; margin: 0; padding: 0; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
            .email-container {{ width: 100%; margin: 0 auto; padding: 20px 0; }}
            .card {{ background-color: #ffffff; max-width: 680px; margin: 0 auto; border: 1px solid #dee2e6; border-radius: 6px; overflow: hidden; box-shadow: 0 0 15px rgba(0,0,0,0.05); }}
            .header-img, .footer-img {{ width: 100%; height: auto; display: block; border: 0; }}
            .content-padding {{ 
                {intended_content_padding_css} /* CSS CHANGE APPLIED HERE */
                line-height: 1.7; 
                color: #333333; 
                font-size: 15px; 
            }}
            .content-padding p {{ 
                margin-top: 0; 
                margin-bottom: 15px; 
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="card">
                <div><img src="cid:header_image" alt="Email Header" class="header-img"></div>
                <div class="content-padding">
                    {processed_html_body}
                </div>
                <div><img src="cid:footer_image" alt="Email Footer" class="footer-img"></div>
            </div>
        </div>
    </body>
    </html>
    """
    msg.attach(MIMEText(email_html_structure, 'html', 'utf-8'))

    # Attach Header Image
    try:
        with open(header_image_path, 'rb') as fp_header:
            img_header = MIMEImage(fp_header.read())
            img_header.add_header('Content-ID', '<header_image>')
            img_header.add_header('Content-Disposition', 'inline', filename=header_image_path.name)
            msg.attach(img_header)
    except FileNotFoundError:
        print(f"Warning: Header image not found at '{header_image_path}'.")
    except Exception as e:
        print(f"Error attaching header image: {e}")

    # Attach Footer Image
    try:
        with open(footer_image_path, 'rb') as fp_footer:
            img_footer = MIMEImage(fp_footer.read())
            img_footer.add_header('Content-ID', '<footer_image>')
            img_footer.add_header('Content-Disposition', 'inline', filename=footer_image_path.name)
            msg.attach(img_footer)
    except FileNotFoundError:
        print(f"Warning: Footer image not found at '{footer_image_path}'.")
    except Exception as e:
        print(f"Error attaching footer image: {e}")

    # Send the Mail (Simplified SMTP interaction)
    try:
        server = smtplib.SMTP(smtp_server_address)
        server.sendmail(sender_email, recipient_emails_list, msg.as_string())
        server.quit()
        print(f"Email sent successfully to {', '.join(recipient_emails_list)} via {smtp_server_address}!")
    except smtplib.SMTPRecipientsRefused as e:
        print(f"Error: All recipients were refused. {e.recipients}")
    except Exception as e:
        print(f"An unexpected error occurred while sending email: {e}")

# --- How to Use (Example) ---
if __name__ == '__main__':
    subject = "System Update (Padding Test 5.0)" # Changed subject for testing

    body_content_simple = """
Hello Team,

This is an important update regarding the recent system maintenance.
Everything is now back online.

Key points to note:
- Service X has been upgraded.
- Service Y performance has improved.

Please report any issues to the support desk.

Thank you for your cooperation.
The IT Department
    """.strip()

    to_email_addresses_str = "your_recipient@example.com"  # << CHANGE THIS
    from_address = "your_sender_email@yourdomain.com"  # << CHANGE THIS
    smtp_server = "your_smtp_server.yourdomain.com" # << CHANGE THIS

    send_templated_email_simplified(
        subject_line=subject,
        plain_text_body=body_content_simple,
        recipient_email_str=to_email_addresses_str,
        sender_email=from_address,
        smtp_server_address=smtp_server
    )
