from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import json
import os
import re
import uuid

app = Flask(__name__, template_folder="templates")

PRODUCTS_FILE = "products.json"
DIST_FILE = "../index.html"


def slugify(text):
    text = (text or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "product"


def make_product_id(product):
    # Prefer image filename if present
    image = (product.get("image") or "").strip()
    if image:
        base = os.path.basename(image)
        stem = os.path.splitext(base)[0]
        if stem:
            return stem

    # Fall back to label/title
    label = product.get("label") or product.get("title") or ""
    return slugify(label)


def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        return []

    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
        products = json.load(f)

    changed = False
    seen_ids = set()

    for product in products:
        product_id = (product.get("id") or "").strip()

        if not product_id:
            product_id = make_product_id(product)

        original_id = product_id
        counter = 2
        while product_id in seen_ids:
            product_id = f"{original_id}-{counter}"
            counter += 1

        if product.get("id") != product_id:
            product["id"] = product_id
            changed = True

        seen_ids.add(product_id)

    if changed:
        save_products(products)

    return products


def save_products(products):
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)


def build_static_index():
    products = load_products()

    with app.app_context():
        rendered = render_template("index.html", products=products)

    with open(DIST_FILE, "w", encoding="utf-8") as f:
        f.write(rendered)

    return DIST_FILE


@app.route("/images/<path:filename>")
def serve_images(filename):
    return send_from_directory("../images", filename)


@app.route("/")
def index():
    products = load_products()
    return render_template("index.html", products=products)


@app.route("/admin")
def admin():
    products = load_products()
    edit_id = request.args.get("edit_id", "").strip()

    editing_product = None
    if edit_id:
        editing_product = next((p for p in products if p.get("id") == edit_id), None)

    return render_template(
        "admin.html",
        products=products,
        editing_product=editing_product
    )


@app.route("/admin/add", methods=["POST"])
def add_product():
    products = load_products()

    label = request.form.get("label", "").strip()
    title = request.form.get("title", "").strip()
    caption = request.form.get("caption", "").strip()
    amazon_url = request.form.get("amazon_url", "").strip()
    image = request.form.get("image", "").strip()
    meta = request.form.get("meta", "Kiki’s pick").strip()

    temp_product = {
        "label": label,
        "title": title,
        "caption": caption,
        "amazon_url": amazon_url,
        "image": image,
        "meta": meta,
    }

    product_id = make_product_id(temp_product)
    original_id = product_id
    counter = 2

    existing_ids = {p.get("id") for p in products}
    while product_id in existing_ids:
        product_id = f"{original_id}-{counter}"
        counter += 1

    new_product = {
        "id": product_id,
        "label": label,
        "title": title,
        "caption": caption,
        "amazon_url": amazon_url,
        "image": image,
        "meta": meta,
    }

    products.insert(0, new_product)
    save_products(products)
    return redirect(url_for("admin"))


@app.route("/admin/update/<product_id>", methods=["POST"])
def update_product(product_id):
    products = load_products()

    for product in products:
        if product.get("id") == product_id:
            product["label"] = request.form.get("label", "").strip()
            product["title"] = request.form.get("title", "").strip()
            product["caption"] = request.form.get("caption", "").strip()
            product["amazon_url"] = request.form.get("amazon_url", "").strip()
            product["image"] = request.form.get("image", "").strip()
            product["meta"] = request.form.get("meta", "Kiki’s pick").strip()

            # keep existing id unless it was blank somehow
            if not product.get("id"):
                product["id"] = make_product_id(product)
            break

    save_products(products)
    return redirect(url_for("admin"))


@app.route("/admin/move/<product_id>/<direction>", methods=["POST"])
def move_product(product_id, direction):
    products = load_products()
    idx = next((i for i, p in enumerate(products) if p.get("id") == product_id), None)

    if idx is not None:
        if direction == "up" and idx > 0:
            products[idx], products[idx - 1] = products[idx - 1], products[idx]
        elif direction == "down" and idx < len(products) - 1:
            products[idx], products[idx + 1] = products[idx + 1], products[idx]

    save_products(products)
    return redirect(url_for("admin"))


@app.route("/admin/delete/<product_id>", methods=["POST"])
def delete_product(product_id):
    products = [p for p in load_products() if p.get("id") != product_id]
    save_products(products)
    return redirect(url_for("admin"))


@app.route("/admin/export", methods=["POST"])
def export_static():
    output_file = build_static_index()
    return f"Exported static HTML to {output_file}"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "7000"))
    app.run(host="0.0.0.0", port=port, debug=True)