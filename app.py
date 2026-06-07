# =========================
# 📌 GEREKLİ KÜTÜPHANELER
# =========================

from flask import Flask, render_template, request, redirect
# Flask → web framework (web sitesi / server oluşturur)
# render_template → HTML dosyalarını ekrana basar (templates klasöründen)
# request → HTML formundan gelen verileri alır
# redirect → kullanıcıyı başka sayfaya yönlendirir

import sqlite3
import os
import time
from werkzeug.utils import secure_filename
# sqlite3 → küçük yerel veritabanı (blog.db dosyası oluşturur ve yönetir)


# =========================
# 🚀 FLASK UYGULAMASINI BAŞLAT
# =========================

app = Flask(__name__)
# Flask uygulamasını oluşturur


# =========================
# 🗃️ VERİTABANI OLUŞTURMA
# =========================

def init_db():
    # blog.db adlı SQLite veritabanına bağlan

    conn = sqlite3.connect("blog.db")
    # Eğer blog.db yoksa otomatik oluşturur

    cur = conn.cursor()
    # SQL komutları yazmak için "imleç" (cursor) oluşturur

    cur.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL
    )
    """)
    # posts tablosunu oluşturur:
    # id → otomatik artan benzersiz numara
    # title → blog başlığı
    # content → blog içeriği
    # IF NOT EXISTS → tablo varsa tekrar oluşturmaz

    conn.commit()
    # yapılan değişiklikleri veritabanına kaydeder

    conn.close()
    # bağlantıyı kapatır

    # Ensure 'image' column exists (for backward compatibility)
    conn = sqlite3.connect("blog.db")
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(posts)")
    cols = [row[1] for row in cur.fetchall()]
    if 'image' not in cols:
        try:
            cur.execute("ALTER TABLE posts ADD COLUMN image TEXT")
            conn.commit()
        except Exception:
            pass
    conn.close()


# uygulama açılır açılmaz tablo hazır olsun
init_db()


# =========================
# 🏠 ANA SAYFA (BLOG LİSTELEME)
# =========================

@app.route("/")
def index():
    # "/" → site ana sayfası (localhost:5000)

    conn = sqlite3.connect("blog.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT id, title, content
        FROM posts
        ORDER BY id DESC
    """)
    # posts tablosundaki tüm yazıları getirir
    # ORDER BY id DESC → en yeni post en üstte olur

    posts = cur.fetchall()
    # tüm sonuçları liste olarak alır

    conn.close()

    return render_template("index.html", posts=posts)
    # index.html dosyasına posts verisini gönderir
    # HTML içinde {{ posts }} olarak kullanılır


# =========================
# 📝 YENİ POST SAYFASI
# =========================

@app.route("/new")
def new_post():
    # kullanıcıya form sayfasını gösterir

    return render_template("new.html")
    # new.html → başlık ve içerik girme formu


# =========================
# 📥 FORM VERİSİ ALMA + KAYDETME
# =========================

@app.route("/create", methods=["POST"])
def create_post():
    # sadece form gönderilince çalışır (POST request)

    title = request.form.get("title")
    content = request.form.get("content")

    # handle uploaded images (multiple)
    image_files = request.files.getlist('images')
    image_filenames = []
    upload_folder = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    for img in image_files:
        if img and img.filename:
            filename = secure_filename(img.filename)
            filename = f"{int(time.time())}_{filename}"
            save_path = os.path.join(upload_folder, filename)
            try:
                img.save(save_path)
                image_filenames.append(filename)
            except Exception:
                pass
    image_filename = '||'.join(image_filenames) if image_filenames else None

    conn = sqlite3.connect("blog.db")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO posts (title, content, image)
        VALUES (?, ?, ?)
    """, (title, content, image_filename))

    conn.commit()
    conn.close()

    return redirect("/")
    # işlem bitince kullanıcıyı ana sayfaya gönderir


# =========================
# 🗑️ POST SİLME
# =========================

@app.route("/delete/<int:post_id>", methods=["POST"])
def delete_post(post_id):
    # Veritabanından post'u sil
    conn = sqlite3.connect("blog.db")
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM posts
        WHERE id = ?
    """, (post_id,))

    conn.commit()
    conn.close()

    return redirect("/")


@app.route('/edit/<int:post_id>')
def edit_post(post_id):
    conn = sqlite3.connect('blog.db')
    cur = conn.cursor()
    cur.execute("SELECT id, title, content, image FROM posts WHERE id = ?", (post_id,))
    post = cur.fetchone()
    conn.close()
    if not post:
        return redirect('/')
    return render_template('edit.html', post=post)


@app.route('/update/<int:post_id>', methods=['POST'])
def update_post(post_id):
    title = request.form.get('title')
    content = request.form.get('content')

    conn = sqlite3.connect('blog.db')
    cur = conn.cursor()
    cur.execute("SELECT image FROM posts WHERE id = ?", (post_id,))
    row = cur.fetchone()
    old_image = row[0] if row else None

    # handle multiple uploaded images for update (append new images)
    image_files = request.files.getlist('images')
    image_filenames = []
    upload_folder = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    for img in image_files:
        if img and img.filename:
            filename = secure_filename(img.filename)
            filename = f"{int(time.time())}_{filename}"
            save_path = os.path.join(upload_folder, filename)
            try:
                img.save(save_path)
                image_filenames.append(filename)
            except Exception:
                pass

    if image_filenames:
        # append new images to existing ones (do not delete previous uploads)
        if old_image:
            try:
                old_list = old_image.split('||') if old_image else []
            except Exception:
                old_list = []
            merged = old_list + image_filenames
            image_filename = '||'.join(merged)
        else:
            image_filename = '||'.join(image_filenames)
    else:
        image_filename = old_image

    cur.execute("""
        UPDATE posts
        SET title = ?, content = ?, image = ?
        WHERE id = ?
    """, (title, content, image_filename, post_id))
    conn.commit()
    conn.close()
    return redirect('/')


@app.route('/post/<int:post_id>')
def show_post(post_id):
    conn = sqlite3.connect('blog.db')
    cur = conn.cursor()
    cur.execute("SELECT id, title, content, image FROM posts WHERE id = ?", (post_id,))
    post = cur.fetchone()
    conn.close()
    if not post:
        return redirect('/')
    return render_template('post.html', post=post)


@app.route('/delete_image/<int:post_id>', methods=['POST'])
def delete_image(post_id):
    filename = request.form.get('filename')
    if not filename:
        return redirect(f"/edit/{post_id}")

    conn = sqlite3.connect('blog.db')
    cur = conn.cursor()
    cur.execute("SELECT image FROM posts WHERE id = ?", (post_id,))
    row = cur.fetchone()
    if row:
        imgs = row[0].split('||') if row[0] else []
        if filename in imgs:
            imgs = [i for i in imgs if i != filename]
            # remove file from uploads folder
            upload_folder = os.path.join(app.root_path, 'static', 'uploads')
            try:
                file_path = os.path.join(upload_folder, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass
            new_value = '||'.join(imgs) if imgs else None
            cur.execute("UPDATE posts SET image = ? WHERE id = ?", (new_value, post_id))
            conn.commit()
    conn.close()
    return redirect(f"/edit/{post_id}")


# =========================
# ▶️ SERVERI ÇALIŞTIR
# =========================

if __name__ == "__main__":
    app.run(debug=True)
    # debug=True:
    # - kod değişince otomatik yenilenir
    # - hata mesajlarını detaylı gösterir