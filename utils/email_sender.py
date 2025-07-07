import os
import sendgrid
from sendgrid.helpers.mail import Mail, From, To, Subject, Content

def send_reset_email(to_email_address, reset_link):
    """Mengirim email reset password menggunakan metode SendGrid yang lebih eksplisit."""
    
    # Inisialisasi API client
    api_key=os.getenv('SENDGRID_API_KEY')
    print(api_key)
    sg = sendgrid.SendGridAPIClient(api_key)
    print(sg)

    # Siapkan konten email
    MAIL_FROM_EMAIL = os.getenv('MAIL_FROM_EMAIL')
    print(MAIL_FROM_EMAIL)
    from_email = From(MAIL_FROM_EMAIL)
    to_email = To(to_email_address)
    subject = Subject("Instruksi Reset Password Anda")
    
    # Buat konten email dalam format HTML
    html_content_string = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
            <h2 style="color: #1e3a8a;">Permintaan Reset Password</h2>
            <p>Kami menerima permintaan untuk mereset password akun Anda. Silakan klik tombol di bawah ini untuk mengatur ulang password Anda:</p>
            <p style="text-align: center;">
                <a href="{reset_link}" target="_blank" style="display: inline-block; padding: 12px 24px; font-size: 16px; color: #fff; background-color: #2563eb; text-decoration: none; border-radius: 5px;">
                    Reset Password
                </a>
            </p>
            <p>Link ini hanya valid selama 1 jam.</p>
            <p>Jika Anda tidak merasa meminta perubahan ini, Anda bisa mengabaikan email ini dengan aman.</p>
        </div>
    </body>
    </html>
    """
    # Gunakan helper Content dengan tipe "text/html"
    content = Content("text/html", html_content_string)

    # Buat objek email
    mail = Mail(from_email, to_email, subject, content)

    try:
        # Kirim email menggunakan metode .post
        response = sg.client.mail.send.post(request_body=mail.get())
        
        # SendGrid biasanya mengembalikan status 202 Accepted jika berhasil
        print(f"Email sent to {to_email_address}. Status code: {response.status_code}")
        # Kita anggap sukses jika status code ada di rentang 200-299
        return 200 <= response.status_code < 300
        
    except Exception as e:
        print(f"Error sending email: {e}")
        # Cetak detail error jika ada
        if hasattr(e, 'body'):
            print(f"SendGrid response body: {e.body}")
        return False