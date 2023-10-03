from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from DigdirRoadmap import DigdirRoadmapItem
import smtplib
import io
import csv


def send_email(subject: str, body, sender: str, recipients: list, password: str, report_file: io.StringIO = None, report_file_name: str = None):

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    html_part = MIMEText(body, 'html')
    msg.attach(html_part)

    if report_file is not None:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(report_file.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {report_file_name}.csv")
        msg.attach(part)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())


def generate_csv(roadmapItems: DigdirRoadmapItem):
    csv_output = io.StringIO()
    csv_writer = csv.writer(csv_output)
    csv_writer.writerow(["Tittel",
                        "Overordnet beskrivelse",
                         "Produkt",
                         "Status",
                         "Start",
                         "End",
                         "Progresjon (%)",
                         "Estimerte ukesverk",
                         "Tasks",
                         "Closed",
                         "Avhengigheter",
                         "URL",
                         "Nye altinn",
                         "BRG",
                         "SKD",
                         "SSB"])
    for roadmap_item in roadmapItems:
        has_nye_altinn_label = 'program/nye-altinn' in roadmap_item.labels
        has_brg_label = 'org/brg' in roadmap_item.labels
        has_skd_label = 'org/skd' in roadmap_item.labels
        has_ssb_label = 'org/ssb' in roadmap_item.labels

        csv_writer.writerow([roadmap_item.title,
                            roadmap_item.task_summary,
                            roadmap_item.product,
                            roadmap_item.status,
                            roadmap_item.start,
                            roadmap_item.end,
                            roadmap_item.progresjon,
                            roadmap_item.estimerte_ukesverk,
                            roadmap_item.numberOfTrackedIssues,
                            roadmap_item.numberOfSovedIssues,
                            roadmap_item.dependencies,
                            roadmap_item.url,
                            has_nye_altinn_label,
                            has_brg_label,
                            has_skd_label,
                            has_ssb_label])
    csv_output.seek(0)
    return csv_output
