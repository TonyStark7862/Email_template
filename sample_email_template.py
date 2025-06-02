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
        # Split by double newlines to create paragraphs
        paragraphs_text = plain_text_body.strip().split('\n\n')
        html_paragraphs_list = []
        for para_content in paragraphs_text:
            para_content_stripped = para_content.strip()
            if para_content_stripped: # Only process non-empty paragraph chunks
                # Escape HTML special characters to prevent them from breaking the layout
                escaped_text = html.escape(para_content_stripped)
                # Convert single newlines within the paragraph to <br> tags
                formatted_text = escaped_text.replace('\n', '<br>\n')
                html_paragraphs_list.append(f"<p>{formatted_text}</p>")
        
        if html_paragraphs_list:
            processed_html_body = "\n".join(html_paragraphs_list)
        else: # Input might have been all whitespace or empty paragraphs
            processed_html_body = "<p>&nbsp;</p>" # Non-breaking space
            
    else: # plain_text_body was None, empty, or only whitespace
        processed_html_body = "<p>&nbsp;</p>" # Default to a non-breaking space paragraph

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
            .content-padding {{ padding: 20px 30px; line-height: 1.7; color: #333333; font-size: 15px; }}
            .content-padding p {{ margin-top: 0; margin-bottom: 15px; }} /* Style for paragraphs */
            /* Add more specific styles if needed for h1, h2, ul, li etc. if you ever plan to allow richer input */
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="card">
                <div><img src="cid:header_image" alt="Email Header" class="header-img"></div>
                <div class="content-padding">
                    {processed_html_body}  {/* Use the auto-formatted HTML body here */}
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
    # (Include other specific SMTP error handling as in the previous version)
    except Exception as e:
        print(f"An unexpected error occurred while sending email: {e}")

# --- How to Use (Example) ---
if __name__ == '__main__':
    subject = "System Update (Plain Text)"

    # Now you provide simple plain text for the body
    # Double newlines create separate paragraphs.
    # Single newlines create line breaks within a paragraph.
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
    """.strip() # .strip() is good practice for multiline strings

    to_email_addresses_str = "your_recipient@example.com,another@example.com"  # << CHANGE THIS
    from_address = "your_sender_email@yourdomain.com"  # << CHANGE THIS
    smtp_server = "your_smtp_server.yourdomain.com" # << CHANGE THIS

    send_templated_email_simplified(
        subject_line=subject,
        plain_text_body=body_content_simple, # Pass the simple text here
        recipient_email_str=to_email_addresses_str,
        sender_email=from_address,
        smtp_server_address=smtp_server
    )
