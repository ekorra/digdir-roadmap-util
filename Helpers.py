from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from DigdirRoadmap import DigdirRoadmapItem
import smtplib
import io
import csv


def send_email(subject: str, body, sender: str, recipients: list, password: str, report_file: io.StringIO, report_file_name: str):

    part = MIMEBase("application", "octet-stream")
    part.set_payload(report_file.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {report_file_name}.csv")

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    html_part = MIMEText(body)
    msg.attach(html_part)
    msg.attach(part)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")


def generate_csv(roadmapItems: DigdirRoadmapItem):
    csv_output = io.StringIO()
    csv_writer = csv.writer(csv_output)
    csv_writer.writerow(["Tittel", "Produkt", "Status", "Start",
                        "End", "Progresjon (%)", "Storypoints", "Issues", "Closed", "URL"])
    for roadmap_item in roadmapItems:
        csv_writer.writerow([roadmap_item.title, roadmap_item.product, roadmap_item.status, roadmap_item.start,
                             roadmap_item.end, roadmap_item.progresjon, roadmap_item.storypoints, roadmap_item.numberOfTrackedIssues, roadmap_item.numberOfSovedIssues, roadmap_item.url])
    csv_output.seek(0)
    return csv_output
