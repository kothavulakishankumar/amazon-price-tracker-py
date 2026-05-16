import requests
from bs4 import BeautifulSoup
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ---------------- HEADERS ----------------

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# ---------------- EMAIL SETTINGS ---------------

MY_EMAIL = "your_email@gmail.com"
MY_PASSWORD = "your_gmail_app_password"
TARGET_EMAIL = "target_email@gmail.com"

# ---------------- AMAZON PRICE SCRAPER ----------------

def get_amazon_price(url):

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=10
        )

        response.raise_for_status()

    except requests.RequestException as e:
        print("[ERROR]", e)
        return {"title": None, "price": None}

    soup = BeautifulSoup(response.text, "html.parser")

    # Product Title
    title_tag = soup.find(id="productTitle")

    if title_tag:
        title = title_tag.get_text(strip=True)
    else:
        title = "Unknown Product"

    # Product Price
    price = None

    whole = soup.find("span", class_="a-price-whole")
    fraction = soup.find("span", class_="a-price-fraction")

    if whole:

        whole_text = whole.get_text(strip=True).replace(",", "")

        if fraction:
            fraction_text = fraction.get_text(strip=True)
        else:
            fraction_text = "00"

        try:
            price = float(f"{whole_text}.{fraction_text}")

        except:
            price = None

    return {
        "title": title,
        "price": price
    }

# ---------------- SEND EMAIL ------------

def send_email(title, current_price, target_price, url):

    msg = MIMEMultipart()

    msg["From"] = MY_EMAIL
    msg["To"] = TARGET_EMAIL
    msg["Subject"] = f"Price Drop Alert - {title}"

    body = f"""
Product: {title}

Current Price: ₹{current_price}

Target Price: ₹{target_price}

Buy Now:
{url}
"""

    msg.attach(MIMEText(body, "plain"))

    try:

        with smtplib.SMTP("smtp.gmail.com", 587) as server:

            server.starttls()

            server.login(
                MY_EMAIL,
                MY_PASSWORD
            )

            server.sendmail(
                MY_EMAIL,
                TARGET_EMAIL,
                msg.as_string()
            )

        print("[SUCCESS] Email Sent!")

    except Exception as e:

        print("[EMAIL ERROR]", e)

# ---------------- PRICE CHECKER ----------------

def check_price(url, target_price):

    while True:

        data = get_amazon_price(url)

        title = data["title"]
        price = data["price"]

        print("Title :", title)
        print("Price :", price)

        # If price dropped
        if price and price <= target_price:

            print("Price Dropped!")

            send_email(
                title,
                price,
                target_price,
                url
            )

            # Stop after email sent
            break

        else:
            print("Price still high.")

        # Wait 6 hours
        time.sleep(21600)

# ---------------- MAIN ----------------

if __name__ == "__main__":

    url = "YOUR_AMAZON_PRODUCT_LINK"

    target_price = 500

    check_price(
        url,
        target_price
    )