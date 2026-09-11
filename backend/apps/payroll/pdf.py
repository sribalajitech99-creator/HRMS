import re
import zipfile
from calendar import month_name
from io import BytesIO

from django.http import HttpResponse

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet

from .services import money
from .utils import amount_in_words, indian_grouping


ACCENT = colors.HexColor("#1B5E20")
ACCENT_LIGHT = colors.HexColor("#E8F0E9")
GREY = colors.HexColor("#374151")
LIGHT_GREY = colors.HexColor("#F3F4F6")
MID_GREY = colors.HexColor("#9CA3AF")
DARK = colors.HexColor("#111827")


def mask_account_number(number):
    """Mask an account number, keeping only the last four digits."""
    digits = re.sub(r"\D", "", str(number or ""))

    if not digits:
        return "—"

    if len(digits) <= 4:
        return f"XXXXXXXX{digits}"

    return f"XXXXXXXX{digits[-4:]}"


def _amount(value):
    return f"Rs. {indian_grouping(money(value))}"


def _build_payslip_story(payslip, styles, mask_bank=True):
    """Return a list of platypus elements for a single payslip."""
    employee = payslip.employee

    story = []

    story.append(Spacer(1, 2 * mm))

    period = (
        f"{month_name[payslip.payroll_run.month]} "
        f"{payslip.payroll_run.year}"
    )

    pay_date = payslip.payroll_run.pay_date

    pay_date_str = (
        pay_date.strftime("%d-%b-%Y")
        if pay_date
        else "—"
    )

    title = Table(
        [[
            Paragraph(
                f"<b>SALARY SLIP</b>",
                styles["Title"],
            )
        ]],
        colWidths=[90 * mm],
    )

    title.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("TEXTCOLOR", (0, 0), (-1, -1), ACCENT),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )

    sub = Table(
        [[
            Paragraph(
                f"For the month of <b>{period}</b>",
                styles["Normal"],
            )
        ]],
        colWidths=[90 * mm],
    )

    sub.setStyle(
        TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )

    title_block = Table(
        [[title], [sub]],
        colWidths=[90 * mm],
    )

    title_block.setStyle(
        TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )

    story.append(title_block)

    story.append(Spacer(1, 4 * mm))

    story.append(
        _summary_section(
            [
                ("Employee", employee.employee_code),
                ("Designation", employee.designation.name if employee.designation_id else "—"),
                ("Department", employee.department.name if employee.department_id else "—"),
                ("Date of Joining", employee.joining_date.strftime("%d-%b-%Y")),
                ("Pay Date", pay_date_str),
            ],
            styles,
        )
    )

    story.append(Spacer(1, 3 * mm))

    earnings = [
        ("Basic Salary", payslip.basic_salary),
        ("Dearness Allowance", payslip.dearness_allowance),
    ]

    earnings = [
        line
        for line in earnings
        if money(line[1]) > 0
    ]

    gross = money(payslip.gross_salary) + money(payslip.overtime_amount)

    deductions = [
        ("PF Deductions", payslip.pf),
        ("Other / Advance", payslip.other_deduction),
        ("LOP Deduction", payslip.lop_deduction),
    ]

    deductions = [
        line
        for line in deductions
        if money(line[1]) > 0
    ]

    total_deductions = money(payslip.deductions)

    story.append(
        _earnings_deductions_table(
            "Earnings",
            earnings,
            "Gross Earnings",
            gross,
            "Deductions",
            deductions,
            "Total Deductions",
            total_deductions,
            styles,
        )
    )

    story.append(Spacer(1, 4 * mm))

    net = money(payslip.net_salary)

    net_table = Table(
        [[
            Paragraph(
                "NET PAY",
                styles["Normal"],
            ),
            Paragraph(
                f"<b>{_amount(net)}</b>",
                styles["Normal"],
            ),
        ]],
        colWidths=[140 * mm, 46 * mm],
    )

    net_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), ACCENT),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 13),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(net_table)

    story.append(Spacer(1, 3 * mm))

    in_words = amount_in_words(net)

    words = Paragraph(
        f"<b>Amount in words:</b> "
        f"<font color='{GREY.hexval().replace('0x', '#')}'>{in_words}</font>",
        styles["Normal"],
    )

    story.append(
        Table(
            [[words]],
            colWidths=[186 * mm],
            style=TableStyle(
                [
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
            ),
        )
    )

    story.append(Spacer(1, 3 * mm))

    story.append(
        _attendance_section(payslip, styles)
    )

    story.append(Spacer(1, 3 * mm))

    story.append(
        _payment_section(
            payslip,
            mask_bank,
            styles,
        )
    )

    return story


def payslip_pdf_response(payslip, mask_bank=True):
    """Generate a professional A4 payslip PDF for a single payslip."""
    buffer = BytesIO()

    styles = getSampleStyleSheet()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
        title=f"Payslip {payslip.employee.employee_code}",
        author="HRMS",
    )

    story = _build_payslip_story(payslip, styles, mask_bank)

    doc.build(story)

    buffer.seek(0)

    response = HttpResponse(
        buffer,
        content_type="application/pdf",
    )

    month = month_name[payslip.payroll_run.month]

    filename = (
        f"Payslip_{payslip.employee.employee_code}_"
        f"{month}_{payslip.payroll_run.year}.pdf"
    )

    response["Content-Disposition"] = (
        'attachment; filename="'
        f"{filename}\""
    )

    return response


def _build_single_payslip_pdf(payslip, mask_bank=True):
    """Return a BytesIO buffer containing a single payslip PDF."""
    buffer = BytesIO()

    styles = getSampleStyleSheet()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
        title=f"Payslip {payslip.employee.employee_code}",
        author="HRMS",
    )

    story = _build_payslip_story(payslip, styles, mask_bank)

    doc.build(story)

    buffer.seek(0)

    return buffer


def bulk_payslip_zip_response(payslips, mask_bank=True):
    """Generate a ZIP archive with one PDF per payslip.

    ``payslips`` should be a queryset or list of Payslip objects
    already fetched with the required related fields.
    """
    payslip_list = list(payslips)

    if not payslip_list:
        return None

    first = payslip_list[0]
    month = month_name[first.payroll_run.month]

    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for payslip in payslip_list:
            emp = payslip.employee
            code = emp.employee_code
            pdf_buf = _build_single_payslip_pdf(payslip, mask_bank)

            zip_filename = (
                f"Payslip_{code}_{month}_"
                f"{payslip.payroll_run.year}.pdf"
            )

            zf.writestr(zip_filename, pdf_buf.read())

    zip_buffer.seek(0)

    filename = (
        f"Payslips_{month}_{first.payroll_run.year}"
        f"_{len(payslip_list)}.zip"
    )

    response = HttpResponse(
        zip_buffer,
        content_type="application/zip",
    )

    response["Content-Disposition"] = (
        'attachment; filename="'
        f"{filename}\""
    )

    return response


def _summary_section(pairs, styles):
    rows = []

    for i in range(0, len(pairs), 3):
        row = []

        for label, value in pairs[i:i + 3]:
            row.append(
                Paragraph(
                    f"<font color='{MID_GREY.hexval().replace('0x', '#')}'>{label}</font>"
                    f"<br/><b>{value}</b>",
                    styles["BodyText"],
                )
            )

        rows.append(row)

    table = Table(
        rows,
        colWidths=[62 * mm, 62 * mm, 62 * mm],
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GREY),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    return table


def _earnings_deductions_table(
    earn_title,
    earnings,
    earn_total_label,
    earn_total,
    ded_title,
    deductions,
    ded_total_label,
    ded_total,
    styles,
):
    max_rows = max(len(earnings), len(deductions))

    header = [
        Paragraph(
            f"<b>{earn_title}</b>",
            styles["BodyText"],
        ),
        "",
        Paragraph(
            f"<b>{ded_title}</b>",
            styles["BodyText"],
        ),
        "",
    ]

    rows = [header]

    for index in range(max_rows):
        earn = earnings[index] if index < len(earnings) else (None, None)
        ded = deductions[index] if index < len(deductions) else (None, None)

        row = [
            Paragraph(
                earn[0] or "",
                styles["BodyText"],
            ),
            Paragraph(
                _amount(earn[1]) if earn[0] else "",
                styles["BodyText"],
            ),
            Paragraph(
                ded[0] or "",
                styles["BodyText"],
            ),
            Paragraph(
                _amount(ded[1]) if ded[0] else "",
                styles["BodyText"],
            ),
        ]

        rows.append(row)

    rows.append(
        [
            Paragraph(
                f"<b>{earn_total_label}</b>",
                styles["BodyText"],
            ),
            Paragraph(
                f"<b>{_amount(earn_total)}</b>",
                styles["BodyText"],
            ),
            Paragraph(
                f"<b>{ded_total_label}</b>",
                styles["BodyText"],
            ),
            Paragraph(
                f"<b>{_amount(ded_total)}</b>",
                styles["BodyText"],
            ),
        ]
    )

    table = Table(
        rows,
        colWidths=[62 * mm, 31 * mm, 62 * mm, 31 * mm],
    )

    style = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("ALIGN", (3, 0), (3, -1), "RIGHT"),
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_GREY),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ("LINEBEFORE", (2, 0), (2, -1), 0.5, colors.HexColor("#D1D5DB")),
        ("LINEABOVE", (0, -1), (-1, -1), 1, DARK),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]

    table.setStyle(TableStyle(style))

    return table


def _attendance_section(payslip, styles):
    items = [
        ("No of Days", payslip.no_of_days),
        ("Working Days", payslip.working_days),
        ("Per Day", payslip.per_day_rate),
        ("Present Days", payslip.present_days),
        ("Paid Leave", payslip.paid_leave_days),
        ("Unpaid Leave / LOP", payslip.lop_days),
        ("Half Days", payslip.half_days),
        ("Holidays", payslip.holidays),
        ("Week Offs", payslip.week_offs),
        ("OT Hours", payslip.ot_hours),
    ]

    rows = []

    for i in range(0, len(items), 3):
        row = []

        for label, value in items[i:i + 3]:
            row.append(
                f"{label}: <b>{value}</b>"
            )

        rows.append([
            Paragraph(
                row[0],
                styles["BodyText"],
            ),
            Paragraph(
                row[1] if len(row) > 1 else "",
                styles["BodyText"],
            ),
            Paragraph(
                row[2] if len(row) > 2 else "",
                styles["BodyText"],
            ),
        ])

    table = Table(
        rows,
        colWidths=[62 * mm, 62 * mm, 62 * mm],
    )

    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]
        )
    )

    return table


def _payment_section(payslip, mask_bank, styles):
    employee = payslip.employee

    account = employee.bank_account_number

    if mask_bank:
        account = mask_account_number(account)

    pay_date = payslip.payroll_run.pay_date

    pay_date_str = (
        pay_date.strftime("%d-%b-%Y")
        if pay_date
        else "—"
    )

    rows = [
        [
            Paragraph(
                "<b>Payment Details</b>",
                styles["BodyText"],
            ),
            "",
        ],
        [
            Paragraph(
                "<b>Pay Date</b>",
                styles["BodyText"],
            ),
            Paragraph(
                f"<b>{pay_date_str}</b>",
                styles["BodyText"],
            ),
        ],
        [
            Paragraph(
                "Bank Name",
                styles["BodyText"],
            ),
            Paragraph(
                f"<b>{employee.bank_name or '—'}</b>",
                styles["BodyText"],
            ),
        ],
        [
            Paragraph(
                "Account Number",
                styles["BodyText"],
            ),
            Paragraph(
                f"<b>{account}</b>",
                styles["BodyText"],
            ),
        ],
        [
            Paragraph(
                "IFSC Code",
                styles["BodyText"],
            ),
            Paragraph(
                f"<b>{employee.ifsc_code or '—'}</b>",
                styles["BodyText"],
            ),
        ],
        [
            Paragraph(
                "Account Holder",
                styles["BodyText"],
            ),
            Paragraph(
                (
                    f"<b>{(employee.first_name + ' ' + employee.last_name).strip()}</b>"
                ),
                styles["BodyText"],
            ),
        ],
    ]

    table = Table(
        rows,
        colWidths=[93 * mm, 93 * mm],
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), ACCENT_LIGHT),
                ("SPAN", (0, 0), (1, 0)),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
                ("LINEBELOW", (0, 1), (-1, -2), 0.25, colors.HexColor("#E5E7EB")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    return table