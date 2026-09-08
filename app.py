import streamlit as st
import requests
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
from datetime import datetime

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:latest"

SYSTEM_PROMPT = """
You are Bizly, a fast and practical AI business assistant.

Help with:
- Business
- Sales and marketing
- Customer replies
- Quotations
- Export and import basics
- Business strategy

Rules:
- Be concise and useful.
- Reply in the user's language.
- Never invent prices, documents, stock or facts.
- Ask if important information is missing.
- Avoid unnecessarily long answers.
"""

st.set_page_config(
    page_title="Bizly AI",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# PROFESSIONAL + RESPONSIVE DESIGN
# =========================================================

st.markdown("""
<style>
/* Main background */
.stApp {
    background: linear-gradient(135deg, #f7f9ff 0%, #eef3ff 55%, #f8fbff 100%);
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1224 0%, #111d3a 55%, #0b142b 100%);
}

section[data-testid="stSidebar"] * {
    color: #f4f7ff;
}

section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.08);
    color: white;
    border-radius: 12px;
    text-align: left;
    min-height: 44px;
    transition: 0.2s;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(82, 111, 255, 0.30);
    border-color: rgba(120,140,255,0.45);
}

/* Hero */
.bizly-hero {
    padding: 28px 32px;
    border-radius: 28px;
    background:
        radial-gradient(circle at 85% 20%, rgba(92,104,255,.18), transparent 28%),
        linear-gradient(135deg, #ffffff 0%, #f0f4ff 100%);
    border: 1px solid #dce4ff;
    box-shadow: 0 18px 50px rgba(40,65,130,.10);
    margin-bottom: 24px;
}

.bizly-badge {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 999px;
    background: #edf1ff;
    color: #3154d8;
    font-weight: 700;
    font-size: 14px;
}

.bizly-title {
    font-size: clamp(38px, 5vw, 68px);
    line-height: 1.02;
    font-weight: 850;
    letter-spacing: -2px;
    color: #101a38;
    margin: 18px 0 12px 0;
}

.bizly-gradient {
    background: linear-gradient(90deg, #3154d8, #6947d9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.bizly-subtitle {
    font-size: clamp(17px, 2vw, 22px);
    color: #60708f;
    max-width: 760px;
}

/* Cards */
.feature-card {
    padding: 24px;
    min-height: 190px;
    border-radius: 22px;
    background: rgba(255,255,255,.86);
    border: 1px solid #dce4f5;
    box-shadow: 0 10px 30px rgba(50,70,120,.08);
}

.feature-icon {
    font-size: 30px;
    margin-bottom: 14px;
}

.feature-title {
    font-size: 21px;
    font-weight: 800;
    color: #172342;
}

.feature-text {
    color: #687793;
    margin-top: 8px;
    line-height: 1.5;
}

/* Search history */
.history-box {
    padding: 18px 20px;
    border-radius: 20px;
    background: rgba(255,255,255,.88);
    border: 1px solid #dce4f5;
    box-shadow: 0 8px 25px rgba(50,70,120,.06);
}

.history-item {
    padding: 10px 14px;
    border-radius: 12px;
    background: #f6f8fd;
    margin-top: 8px;
    color: #35425f;
}

/* Inputs */
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div,
div[data-baseweb="select"] > div {
    border-radius: 13px !important;
}

/* Buttons */
.stButton > button, .stDownloadButton > button {
    border-radius: 13px;
    min-height: 44px;
    font-weight: 700;
}

/* Mobile */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem 0.8rem 2rem 0.8rem;
    }

    .bizly-hero {
        padding: 22px 20px;
        border-radius: 22px;
    }

    .bizly-title {
        font-size: 40px;
        letter-spacing: -1.2px;
    }

    .feature-card {
        min-height: auto;
        padding: 19px;
    }

    section[data-testid="stSidebar"] {
        min-width: 280px;
        max-width: 88vw;
    }
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# OLLAMA
# =========================================================

def ask_ollama(messages):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": messages,
            "stream": False,
            "options": {"num_predict": 400}
        },
        timeout=300
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


# =========================================================
# QUOTATION PDF
# =========================================================

def create_quotation_pdf(
    customer_name,
    company_name,
    product_name,
    quantity,
    price,
    payment_terms,
    delivery_details
):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    title = styles["Title"]
    title.alignment = TA_CENTER
    normal = styles["Normal"]

    story = []

    quotation_number = "BIZ-" + datetime.now().strftime("%Y%m%d%H%M")
    date = datetime.now().strftime("%d-%m-%Y")
    total = quantity * price

    story.append(Paragraph("BIZLY", title))
    story.append(Paragraph("Professional Business Quotation", title))
    story.append(Spacer(1, 20))

    story.append(Paragraph(
        f"<b>Quotation No:</b> {quotation_number}<br/>"
        f"<b>Date:</b> {date}",
        normal
    ))
    story.append(Spacer(1, 15))

    story.append(Paragraph(
        f"<b>Customer:</b> {customer_name}<br/>"
        f"<b>Company:</b> {company_name}",
        normal
    ))
    story.append(Spacer(1, 20))

    table_data = [
        ["Product", "Quantity", "Unit Price", "Total"],
        [product_name, str(quantity), f"₹{price:,.2f}", f"₹{total:,.2f}"]
    ]

    table = Table(table_data, colWidths=[230, 70, 90, 90])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8)
    ]))

    story.append(table)
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"<b>Total Amount: ₹{total:,.2f}</b>", normal))

    if payment_terms:
        story.append(Paragraph(
            f"<b>Payment Terms:</b> {payment_terms}", normal
        ))

    if delivery_details:
        story.append(Paragraph(
            f"<b>Delivery:</b> {delivery_details}", normal
        ))

    story.append(Spacer(1, 30))
    story.append(Paragraph("Thank you for your business.", normal))
    story.append(Spacer(1, 15))
    story.append(Paragraph("Generated by Bizly AI", normal))

    doc.build(story)
    buffer.seek(0)
    return buffer


# =========================================================

# =========================================================
# GST TAX INVOICE PDF
# =========================================================

def create_gst_invoice_pdf(seller_name, seller_gstin, seller_address, seller_state,
                           invoice_no, invoice_date, place_of_supply, supply_type,
                           buyer_name, buyer_gstin, buyer_address,
                           items, discount, notes, bank_details):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=28, leftMargin=28, topMargin=28, bottomMargin=28)
    styles = getSampleStyleSheet()
    title = styles["Title"]
    title.alignment = TA_CENTER
    title.fontSize = 18
    normal = styles["Normal"]
    normal.fontSize = 8.5
    normal.leading = 11
    small = styles["Normal"].clone("small_invoice")
    small.fontSize = 7.5
    small.leading = 9
    story = []

    subtotal = sum(i["amount"] for i in items)
    taxable_value = max(subtotal - discount, 0)
    factor = taxable_value / subtotal if subtotal else 1
    cgst_total = sgst_total = igst_total = 0.0
    rows = []

    for idx, item in enumerate(items, 1):
        taxable = item["amount"] * factor
        gst = taxable * item["gst"] / 100
        if supply_type == "Intra-state":
            cgst = sgst = gst / 2
            igst = 0
        else:
            cgst = sgst = 0
            igst = gst
        cgst_total += cgst
        sgst_total += sgst
        igst_total += igst
        rows.append([str(idx), item["name"], item["hsn"], str(item["qty"]),
                     f'Rs. {item["rate"]:,.2f}', f'{item["gst"]:.2f}%', f'Rs. {taxable:,.2f}'])

    gst_total = cgst_total + sgst_total + igst_total
    grand_total = taxable_value + gst_total

    header = Table([
        [Paragraph("<b>BIZLY</b>", title), Paragraph("<b>TAX INVOICE</b>", title)],
        [Paragraph(f"<b>{seller_name or '-'} </b><br/>GSTIN: {seller_gstin or '-'}<br/>{seller_address or '-'}<br/>State: {seller_state or '-'}", normal),
         Paragraph(f"<b>Invoice No:</b> {invoice_no}<br/><b>Invoice Date:</b> {invoice_date}<br/><b>Place of Supply:</b> {place_of_supply or '-'}<br/><b>Supply:</b> {supply_type}", normal)]
    ], colWidths=[275, 255])
    header.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#111d3a")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("BOX", (0,0), (-1,-1), 0.8, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0,1), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 10), ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING", (0,0), (-1,-1), 8), ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story += [header, Spacer(1, 12)]

    buyer = Table([
        [Paragraph("<b>BILL TO</b>", normal), Paragraph("<b>GSTIN</b>", normal)],
        [Paragraph(f"<b>{buyer_name or '-'}</b><br/>{buyer_address or '-'}", normal), Paragraph(buyer_gstin or "-", normal)]
    ], colWidths=[395, 135])
    buyer.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#eef3ff")),
        ("BOX", (0,0), (-1,-1), 0.7, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0,0), (-1,-1), 0.4, colors.HexColor("#dbe3ef")),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story += [buyer, Spacer(1, 12)]

    data = [["#", "Item / Description", "HSN/SAC", "Qty", "Rate", "GST %", "GST Amount", "Taxable Value", "Total"]] + rows
    table = Table(data, colWidths=[25, 170, 65, 40, 72, 45, 93], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#111d3a")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ("ALIGN", (0,0), (0,-1), "CENTER"), ("ALIGN", (3,1), (6,-1), "RIGHT"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("FONTSIZE", (0,0), (-1,-1), 7.5),
        ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story += [table, Spacer(1, 10)]

    tax_rows = [["Subtotal", f"Rs. {subtotal:,.2f}"], ["Discount", f"Rs. {discount:,.2f}"], ["Taxable Value", f"Rs. {taxable_value:,.2f}"]]
    if supply_type == "Intra-state":
        tax_rows += [["CGST", f"Rs. {cgst_total:,.2f}"], ["SGST", f"Rs. {sgst_total:,.2f}"]]
    else:
        tax_rows += [["IGST", f"Rs. {igst_total:,.2f}"]]
    tax_rows += [["Grand Total", f"Rs. {grand_total:,.2f}"]]
    totals = Table(tax_rows, colWidths=[115, 130], hAlign="RIGHT")
    totals.setStyle(TableStyle([
        ("BOX", (0,0), (-1,-1), 0.7, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0,0), (-1,-1), 0.4, colors.HexColor("#e2e8f0")),
        ("ALIGN", (1,0), (1,-1), "RIGHT"), ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),
        ("BACKGROUND", (0,-1), (-1,-1), colors.HexColor("#eef3ff")), ("FONTSIZE", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story += [totals, Spacer(1, 12)]

    footer = Table([
        [Paragraph("<b>Notes / Terms</b><br/>" + (notes or "-"), small), Paragraph("<b>Bank / Payment Details</b><br/>" + (bank_details or "-"), small)],
        [Paragraph("<b>Declaration</b><br/>We declare that this invoice shows the actual price of the goods/services described and that the particulars are true and correct.", small), Paragraph("<br/><br/><b>For " + (seller_name or "Seller") + "</b><br/><br/>Authorized Signatory", small)]
    ], colWidths=[265, 265])
    footer.setStyle(TableStyle([
        ("BOX", (0,0), (-1,-1), 0.7, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0,0), (-1,-1), 0.4, colors.HexColor("#e2e8f0")), ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 8), ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story += [footer, Spacer(1, 8), Paragraph("Generated by Bizly AI • Verify invoice details and applicable GST requirements before issuing.", small)]
    doc.build(story)
    buffer.seek(0)
    return buffer

# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "tool" not in st.session_state:
    st.session_state.tool = "home"

if "search_history" not in st.session_state:
    st.session_state.search_history = []


def add_history(text):
    text = text.strip()
    if not text:
        return

    st.session_state.search_history = [
        item for item in st.session_state.search_history
        if item != text
    ]

    st.session_state.search_history.insert(0, text)
    st.session_state.search_history = st.session_state.search_history[:20]


def go_to(tool):
    st.session_state.tool = tool
    st.rerun()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown("## 💼 Bizly AI")
    st.caption("Your Smart Business Assistant")
    st.divider()

    if st.button("⌂  Home", use_container_width=True):
        go_to("home")

    if st.button("💬  New Chat", use_container_width=True):
        st.session_state.messages = []
        go_to("chat")

    if st.button("📄  Quotation", use_container_width=True):
        go_to("quotation")

    if st.button("🧾  GST Bill", use_container_width=True):
        go_to("gst_bill")

    if st.button("📊  Sales & Marketing", use_container_width=True):
        go_to("sales")

    if st.button("💬  Customer Reply", use_container_width=True):
        go_to("customer")

    if st.button("🌐  Export Help", use_container_width=True):
        go_to("export")

    st.divider()

    st.markdown("### 🔎 Search History")

    if not st.session_state.search_history:
        st.caption("Your recent searches will appear here.")
    else:
        for i, item in enumerate(st.session_state.search_history[:8]):
            short = item if len(item) <= 45 else item[:45] + "..."
            if st.button(
                f"🔍 {short}",
                key=f"history_{i}",
                use_container_width=True
            ):
                st.session_state.tool = "chat"
                st.session_state.pending_query = item
                st.rerun()

        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.search_history = []
            st.rerun()

    st.divider()
    st.caption("Powered by Ollama + Llama 3.2")


# =========================================================
# HOME
# =========================================================

if st.session_state.tool == "home":

    st.markdown("""
    <div class="bizly-hero">
        <span class="bizly-badge">✦ Welcome to Bizly AI</span>
        <div class="bizly-title">
            Your Smart<br>
            <span class="bizly-gradient">AI Business Assistant</span>
        </div>
        <div class="bizly-subtitle">
            Create, communicate and grow — with instant AI support
            for business, marketing, customer replies, quotations and export.
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)

    cards = [
        ("💬", "AI Chat", "Ask anything about your business."),
        ("📄", "Create Quotation", "Generate professional quotations quickly."),
        ("🧾", "GST Bill", "Create GST invoices with automatic tax calculation."),
        ("📊", "Sales & Marketing", "Get practical strategies and content ideas."),
        ("🌍", "Export Help", "Get guidance for international business and export.")
    ]

    for col, (icon, title, text) in zip([c1, c2, c3, c4, c5], cards):
        with col:
            st.markdown(
                f"""
                <div class="feature-card">
                    <div class="feature-icon">{icon}</div>
                    <div class="feature-title">{title}</div>
                    <div class="feature-text">{text}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.write("")
    st.markdown(
        "<h3 style='text-align:center;color:#172342;'>✦ What can I help you with today?</h3>",
        unsafe_allow_html=True
    )

    home_query = st.text_input(
        "Ask Bizly",
        placeholder="Ask Bizly anything...",
        label_visibility="collapsed"
    )

    if st.button("🚀 Ask Bizly", use_container_width=True):
        if home_query.strip():
            add_history(home_query)
            st.session_state.messages = [
                {"role": "user", "content": home_query}
            ]
            st.session_state.tool = "chat"
            st.rerun()

    if st.session_state.search_history:
        st.write("")
        st.markdown(
            "<div class='history-box'><b>🕘 Recent Search History</b></div>",
            unsafe_allow_html=True
        )

        for item in st.session_state.search_history[:4]:
            st.markdown(
                f"<div class='history-item'>🔍 {item}</div>",
                unsafe_allow_html=True
            )


# =========================================================
# QUOTATION
# =========================================================

elif st.session_state.tool == "quotation":

    st.title("📄 Quotation Generator")
    st.caption("Create a professional quotation and download it as PDF.")

    customer_name = st.text_input("Customer Name")
    company_name = st.text_input("Company Name")
    product_name = st.text_input("Product Name")

    col1, col2 = st.columns(2)

    with col1:
        quantity = st.number_input("Quantity", min_value=1, value=1)

    with col2:
        price = st.number_input(
            "Price per Unit (₹)",
            min_value=0.0,
            value=0.0
        )

    payment_terms = st.text_input(
        "Payment Terms",
        placeholder="Example: 50% advance"
    )

    delivery_details = st.text_input(
        "Delivery / Shipping",
        placeholder="Example: Within 15 days"
    )

    if st.button("✨ Generate Quotation", use_container_width=True):
        if not customer_name or not product_name or price <= 0:
            st.warning("Please enter Customer Name, Product Name and Price.")
        else:
            total = quantity * price
            st.success("Quotation generated!")

            st.write(f"**Customer:** {customer_name}")
            st.write(f"**Company:** {company_name}")
            st.write(f"**Product:** {product_name}")
            st.write(f"**Quantity:** {quantity}")
            st.write(f"**Price:** ₹{price:,.2f}")
            st.write(f"**Total:** ₹{total:,.2f}")

            pdf_file = create_quotation_pdf(
                customer_name,
                company_name,
                product_name,
                quantity,
                price,
                payment_terms,
                delivery_details
            )

            st.download_button(
                "📥 Download Quotation PDF",
                data=pdf_file,
                file_name="Bizly_Quotation.pdf",
                mime="application/pdf",
                use_container_width=True
            )


# =========================================================
# SALES & MARKETING
# =========================================================

elif st.session_state.tool == "gst_bill":

    st.title("🧾 GST Tax Invoice")
    st.caption("Professional invoice • automatic GST calculation • PDF download")

    st.markdown("### 🏢 Seller Details")
    c1, c2 = st.columns(2)
    with c1:
        seller_name = st.text_input("Business / Seller Name", key="gst_seller_name")
        seller_gstin = st.text_input("Seller GSTIN", key="gst_seller_gstin", placeholder="22AAAAA0000A1Z5")
        seller_state = st.text_input("Seller State", key="gst_seller_state", placeholder="Uttar Pradesh")
    with c2:
        seller_address = st.text_area("Seller Address", key="gst_seller_address", height=100)
        invoice_no = st.text_input("Invoice Number", key="gst_invoice_no", value="BIZ-" + datetime.now().strftime("%Y%m%d%H%M"))
        invoice_date = st.date_input("Invoice Date", key="gst_invoice_date")

    st.markdown("### 👤 Customer Details")
    c1, c2 = st.columns(2)
    with c1:
        buyer_name = st.text_input("Customer / Buyer Name", key="gst_buyer_name")
        buyer_gstin = st.text_input("Customer GSTIN (optional)", key="gst_buyer_gstin")
    with c2:
        buyer_address = st.text_area("Customer Address", key="gst_buyer_address", height=100)
        place_of_supply = st.text_input("Place of Supply", key="gst_place_of_supply", placeholder="Uttar Pradesh (09)")

    c1, c2 = st.columns(2)
    with c1:
        supply_type = st.selectbox("GST Type", ["Intra-state", "Inter-state"], key="gst_supply_type", help="Intra-state = CGST + SGST. Inter-state = IGST.")
    with c2:
        discount = st.number_input("Overall Discount (₹)", min_value=0.0, value=0.0, step=100.0, key="gst_discount")

    st.markdown("### 📦 Items")
    st.caption("Add up to 5 items. Tax is calculated automatically.")
    items = []
    for i in range(1, 6):
        with st.container(border=True):
            st.markdown(f"**Item {i}**")
            c1, c2, c3 = st.columns([3, 1.3, 1.3])
            with c1:
                item_name = st.text_input("Item / Description", key=f"gst_item_name_{i}")
            with c2:
                hsn = st.text_input("HSN/SAC", key=f"gst_hsn_{i}")
            with c3:
                gst_rate = st.selectbox("GST %", [0, 5, 12, 18, 28], index=3, key=f"gst_rate_{i}")
            c1, c2, c3 = st.columns(3)
            with c1:
                qty = st.number_input("Quantity", min_value=0.0, value=1.0, step=1.0, key=f"gst_qty_{i}")
            with c2:
                rate = st.number_input("Rate / Unit (₹)", min_value=0.0, value=0.0, step=100.0, key=f"gst_rate_unit_{i}")
            with c3:
                amount = qty * rate
                st.metric("Line Amount", f"₹{amount:,.2f}")
            if item_name.strip() and qty > 0 and rate > 0:
                items.append({"name": item_name.strip(), "hsn": hsn.strip() or "-", "gst": float(gst_rate), "qty": qty, "rate": rate, "amount": amount})

    st.markdown("### 💳 Payment & Notes")
    c1, c2 = st.columns(2)
    with c1:
        bank_details = st.text_area("Bank / UPI / Payment Details", placeholder="Bank: ...\nA/C No: ...\nIFSC: ...\nUPI: ...", height=110)
    with c2:
        notes = st.text_area("Notes / Terms & Conditions", placeholder="Payment due within 15 days.", height=110)

    if items:
        subtotal_preview = sum(i["amount"] for i in items)
        taxable_preview = max(subtotal_preview - discount, 0)
        factor_preview = taxable_preview / subtotal_preview if subtotal_preview else 1
        gst_preview = sum(i["amount"] * factor_preview * i["gst"] / 100 for i in items)
        grand_preview = taxable_preview + gst_preview
        st.markdown("### 📊 Invoice Summary")
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Subtotal", f"₹{subtotal_preview:,.2f}")
        s2.metric("Taxable Value", f"₹{taxable_preview:,.2f}")
        s3.metric("GST", f"₹{gst_preview:,.2f}")
        s4.metric("Grand Total", f"₹{grand_preview:,.2f}")

    if st.button("✨ Generate GST Bill PDF", use_container_width=True, type="primary"):
        if not seller_name.strip() or not seller_gstin.strip() or not buyer_name.strip():
            st.warning("Please enter Seller Name, Seller GSTIN and Customer Name.")
        elif not items:
            st.warning("Please add at least one item with name, quantity and rate.")
        elif discount > sum(i["amount"] for i in items):
            st.warning("Discount cannot be greater than the item subtotal.")
        else:
            with st.spinner("Preparing your professional GST invoice..."):
                pdf_file = create_gst_invoice_pdf(seller_name, seller_gstin, seller_address, seller_state, invoice_no, invoice_date.strftime("%d-%m-%Y"), place_of_supply, supply_type, buyer_name, buyer_gstin, buyer_address, items, discount, notes, bank_details)
            st.success("GST Tax Invoice generated successfully!")
            st.download_button("📥 Download GST Bill PDF", data=pdf_file, file_name=f"Bizly_GST_Invoice_{invoice_no}.pdf", mime="application/pdf", use_container_width=True)

elif st.session_state.tool == "sales":

    st.title("📊 Sales & Marketing")
    st.caption("Create practical marketing strategies with Bizly.")

    business = st.text_input(
        "Business / Product",
        placeholder="Example: Handmade handicrafts"
    )

    target = st.text_input(
        "Target Customer",
        placeholder="Example: Boutiques and gift shops"
    )

    platform = st.selectbox(
        "Platform",
        ["Instagram", "WhatsApp", "Facebook", "Google", "Multiple Platforms"]
    )

    goal = st.selectbox(
        "Goal",
        ["More Sales", "More Customers", "More Leads", "Brand Awareness"]
    )

    if st.button("✨ Generate Marketing Plan", use_container_width=True):
        if not business or not target:
            st.warning("Please enter Business/Product and Target Customer.")
        else:
            prompt = f"""
Create a SHORT practical marketing plan.

Business: {business}
Target customer: {target}
Platform: {platform}
Goal: {goal}

Give only:
1. Strategy
2. 3 content ideas
3. 2 ad ideas
4. 3 ways to get customers
5. 7-day action plan

Keep it concise and practical.
"""
            add_history(f"Marketing plan: {business}")

            try:
                with st.spinner("Bizly is creating the plan..."):
                    result = ask_ollama([
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ])
                st.success("Marketing plan ready!")
                st.markdown(result)
            except Exception as e:
                st.error(f"Error: {e}")


# =========================================================
# CUSTOMER REPLY
# =========================================================

elif st.session_state.tool == "customer":

    st.title("📩 Customer Reply")
    st.caption("Turn customer messages into professional ready-to-send replies.")

    customer_message = st.text_area(
        "Customer Message",
        placeholder="Paste customer's message here..."
    )

    language = st.selectbox(
        "Language",
        ["Same as customer", "English", "Hindi"]
    )

    tone = st.selectbox(
        "Tone",
        ["Professional", "Friendly", "Short"]
    )

    channel = st.selectbox(
        "Channel",
        ["WhatsApp", "Email"]
    )

    if st.button("✨ Generate Reply", use_container_width=True):
        if not customer_message.strip():
            st.warning("Please enter the customer's message.")
        else:
            prompt = f"""
Write a short ready-to-send business reply.

Customer message:
{customer_message}

Language: {language}
Tone: {tone}
Channel: {channel}

Do not invent prices, stock or delivery details.
If information is missing, ask politely.
"""
            add_history("Customer reply: " + customer_message[:60])

            try:
                with st.spinner("Bizly is writing..."):
                    reply = ask_ollama([
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ])

                st.success("Reply ready!")
                st.text_area("Your Reply", value=reply, height=180)
            except Exception as e:
                st.error(f"Error: {e}")


# =========================================================
# EXPORT HELP
# =========================================================

elif st.session_state.tool == "export":

    st.title("🌍 Export Assistant")
    st.caption("Practical guidance for exporting from India.")

    export_question = st.text_area(
        "Your Export Question",
        placeholder="Example: India se handicrafts export karne ke liye kaunse documents chahiye?"
    )

    export_topic = st.selectbox(
        "Topic",
        [
            "Export Documents",
            "IEC / GST / RCMC",
            "Shipping",
            "International Payments",
            "Finding Foreign Buyers",
            "Export Quotation",
            "General Export Help"
        ]
    )

    if st.button("✨ Get Export Answer", use_container_width=True):
        if not export_question.strip():
            st.warning("Please enter your export question.")
        else:
            prompt = f"""
Answer this export question for an Indian business.

Question:
{export_question}

Topic:
{export_topic}

Give a concise practical answer.
Mention when the user should verify current rules with official authorities.
Do not invent requirements.
"""
            add_history("Export: " + export_question[:60])

            try:
                with st.spinner("Bizly is preparing your answer..."):
                    answer = ask_ollama([
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ])

                st.success("Export answer ready!")
                st.markdown(answer)
            except Exception as e:
                st.error(f"Error: {e}")


# =========================================================
# GENERAL CHAT
# =========================================================

elif st.session_state.tool == "chat":

    st.title("💬 Bizly AI Chat")
    st.caption("Your private local business assistant powered by Ollama.")

    # Open a history item when clicked from sidebar
    if "pending_query" in st.session_state:
        pending = st.session_state.pop("pending_query")
        if not st.session_state.messages:
            st.session_state.messages.append({
                "role": "user",
                "content": pending
            })

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_message = st.chat_input("Ask Bizly anything...")

    if user_message:
        add_history(user_message)

        st.session_state.messages.append({
            "role": "user",
            "content": user_message
        })

        with st.chat_message("user"):
            st.write(user_message)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(st.session_state.messages)

        try:
            with st.chat_message("assistant"):
                with st.spinner("Bizly is thinking..."):
                    answer = ask_ollama(messages)
                    st.write(answer)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })

        except Exception as e:
            st.error(f"Error: {e}")
