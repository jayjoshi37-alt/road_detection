from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import csv
import io
import numpy as np
import cv2
import os
from werkzeug.utils import secure_filename
from utility.pothole_detector import PotholeDetector
from flask_mysqldb import MySQL
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from utility.crack_detector import CrackDetector
from dotenv import load_dotenv
import os

load_dotenv()
# -------------------- CONFIG --------------------
app = Flask(__name__)

# Secret Key
app.secret_key = os.getenv("SECRET_KEY")

# MySQL Configuration
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

# SMTP Configuration
app.config['SMTP_HOST'] = os.getenv('SMTP_HOST')
app.config['SMTP_PORT'] = int(os.getenv('SMTP_PORT'))
app.config['SMTP_USER'] = os.getenv('SMTP_USER')
app.config['SMTP_PASSWORD'] = os.getenv('SMTP_PASSWORD')
app.config['SMTP_SENDER'] = os.getenv('SMTP_SENDER')
app.config['SMTP_DEBUG'] = int(os.getenv('SMTP_DEBUG', 0))


mysql = MySQL(app)

pothole_detector = PotholeDetector(model_path="model/pothole_model.pt", conf=0.25)
crack_detector   = CrackDetector(model_path="model/crack_model.pt", conf=0.25)

# ===========================
# ROUTES
# ===========================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    # 1. Handle GET request: Display the registration form
    if request.method == "GET":
        return render_template("Registration.html")

    if request.method == "POST":
        # 2. Handle POST request: Process registration data
        first_name = request.form["txtfirst_name"]
        last_name = request.form["txtlast_name"]
        email = request.form["txtemail"].strip().lower()
        organization = request.form["txtorganization"]
        user_type = request.form["txtuser_type"]
        password_hash = generate_password_hash(request.form["txtpassword"])
        confirm_password = request.form["txtconfirm_password"]

        # Database Insertion
        cur = mysql.connection.cursor()
        #cur.execute("INSERT INTO users (first_name, last_name) VALUES (%s, %s,)",(first_name, last_name,))
        cur.execute("INSERT INTO users (first_name, last_name, email, organization, user_type, password_hash) VALUES (%s, %s, %s, %s, %s, %s)",(first_name, last_name, email, organization, user_type, password_hash))
        mysql.connection.commit()
        cur.close()

        # Success
        flash("Registration successful. Please login.", "success")
        return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("Login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not email or not password:
        flash("Email and password are required.", "error")
        return render_template("Login.html"), 400

    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT id, first_name, last_name, email, organization, user_type, password_hash FROM users WHERE email=%s",
        (email,)
    )
    row = cur.fetchone()
    cur.close()

    if not row:
        flash("Invalid email or password.", "error")
        return render_template("Login.html"), 401

    user = {
        "id": row[0],
        "first_name": row[1],
        "last_name": row[2],
        "email": row[3],
        "organization": row[4],
        "user_type": row[5],
        "password_hash": row[6],
    }

    if not check_password_hash(user["password_hash"], password):
        flash("Invalid email or password.", "error")
        return render_template("Login.html"), 401

    session["user_id"] = user["id"]
    session["user_name"] = f"{user['first_name']} {user['last_name']}"
    session["user_email"] = user["email"]
    return redirect(url_for("user_dashboard"))

@app.route("/user/dashboard")
def user_dashboard():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT id, first_name, last_name, email, organization, user_type, created_at, avatar FROM users WHERE id=%s",
        (user_id,)
    )
    row = cur.fetchone()
    cur.close()

    if not row:
        flash("User not found.", "error")
        return redirect(url_for("logout"))

    user = {
        "id": row[0],
        "first_name": row[1],
        "last_name": row[2],
        "email": row[3],
        "organization": row[4],
        "user_type": row[5],
        "created_at": row[6],
        "avatar": row[7] if len(row) > 7 else None,
    }

    user_avatar_url = _user_avatar_url(user_id, user.get("avatar"))

    cur = mysql.connection.cursor()
    cur.execute(
        """
        SELECT id, category, location_text, priority, status, created_at
        FROM complaints
        WHERE user_id=%s
        ORDER BY created_at DESC
        LIMIT 8
        """,
        (user_id,)
    )
    rows = cur.fetchall()
    cur.close()

    recent_complaints = []
    for r in (rows or []):
        recent_complaints.append({
            "id": r[0],
            "category": r[1] or "",
            "location_text": r[2] or "",
            "priority": (r[3] or "low"),
            "status": (r[4] or "New"),
            "created_at": r[5],
        })

    return render_template(
        "user/dashboard.html",
        user=user,
        user_avatar_url=user_avatar_url,
        recent_complaints=recent_complaints,
    )

@app.route("/user/dashboard/stats")
def user_dashboard_stats():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    try:
        cur = mysql.connection.cursor()
        cur.execute(
            """
            SELECT
                COUNT(*) AS total,
                COUNT(DISTINCT NULLIF(TRIM(location_text), '')) AS locations,
                SUM(CASE WHEN LOWER(COALESCE(status,'')) IN ('resolved','closed') THEN 1 ELSE 0 END) AS resolved,
                SUM(CASE WHEN LOWER(COALESCE(status,'')) NOT IN ('resolved','closed') THEN 1 ELSE 0 END) AS pending
            FROM complaints
            WHERE user_id=%s
            """,
            (user_id,),
        )
        row = cur.fetchone()
        cur.close()

        total = int(row[0] or 0) if row else 0
        locations = int(row[1] or 0) if row else 0
        resolved = int(row[2] or 0) if row else 0
        pending = int(row[3] or 0) if row else 0

        return jsonify({
            "success": True,
            "total_detections": total,
            "roads_monitored": locations,
            "repairs_completed": resolved,
            "pending_actions": pending,
        })
    except Exception as e:
        try:
            cur.close()
        except Exception:
            pass
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/user/dashboard/damage-types")
def user_dashboard_damage_types():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    try:
        days_raw = request.args.get("days", "7")
        try:
            days = int(days_raw)
        except Exception:
            days = 7
        days = max(1, min(365, days))

        cur = mysql.connection.cursor()
        cur.execute(
            """
            SELECT
                COALESCE(NULLIF(TRIM(category), ''), 'Other') AS label,
                COUNT(*) AS cnt
            FROM complaints
            WHERE user_id=%s
              AND created_at >= (NOW() - INTERVAL %s DAY)
            GROUP BY COALESCE(NULLIF(TRIM(category), ''), 'Other')
            ORDER BY cnt DESC
            LIMIT 2
            """,
            (user_id, days),
        )
        rows = cur.fetchall()

        cur.execute(
            """
            SELECT COUNT(*)
            FROM complaints
            WHERE user_id=%s
              AND created_at >= (NOW() - INTERVAL %s DAY)
            """,
            (user_id, days),
        )
        total_row = cur.fetchone()
        cur.close()

        total = int(total_row[0] or 0) if total_row else 0
        items = []
        for label, cnt in (rows or []):
            c = int(cnt or 0)
            pct = (c * 100.0 / total) if total > 0 else 0.0
            items.append({"label": str(label), "count": c, "percent": pct})

        return jsonify({
            "success": True,
            "days": days,
            "total": total,
            "items": items,
        })
    except Exception as e:
        try:
            cur.close()
        except Exception:
            pass
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/user/map")
def user_map():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))
    return render_template("user/map.html")

@app.route("/user/analytics")
def user_analytics():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))
    return render_template("user/analytics.html")

@app.route("/user/reports")
def user_reports():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))
    # Fetch user's complaints with basic fields
    cur = mysql.connection.cursor()
    cur.execute(
        """
        SELECT id, title, category, location_text, priority, status, created_at, description, contact, latitude, longitude
        FROM complaints
        WHERE user_id=%s
        ORDER BY created_at DESC
        """,
        (user_id,)
    )
    rows = cur.fetchall()

    complaints = []
    complaint_ids = []
    for r in rows:
        c = {
            "id": r[0],
            "title": r[1],
            "category": r[2],
            "location_text": r[3],
            "priority": r[4],
            "status": r[5] or "New",
            "created_at": r[6],
            "description": r[7],
            "contact": r[8],
            "latitude": r[9],
            "longitude": r[10],
            "images": [],
            "replies": [],
        }
        complaints.append(c)
        complaint_ids.append(r[0])

    # Fetch images for these complaints (if any)
    if complaint_ids:
        # Build placeholders for IN clause
        placeholders = ",".join(["%s"] * len(complaint_ids))
        cur.execute(
            f"SELECT complaint_id, filename FROM complaint_images WHERE complaint_id IN ({placeholders})",
            complaint_ids,
        )
        img_rows = cur.fetchall()
        images_by_cid = {}
        for cid, fname in img_rows:
            images_by_cid.setdefault(cid, []).append(fname)
        # Attach to complaints
        for c in complaints:
            c["images"] = images_by_cid.get(c["id"], [])

        # Ensure tables exist and fetch admin replies for these complaints
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS complaint_replies (
              id INT AUTO_INCREMENT PRIMARY KEY,
              complaint_id INT NOT NULL,
              message TEXT NOT NULL,
              admin_username VARCHAR(100),
              created_at DATETIME NOT NULL,
              INDEX idx_complaint_id (complaint_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        cur.execute(
            f"""
            SELECT id, complaint_id, message, admin_username, created_at
            FROM complaint_replies
            WHERE complaint_id IN ({placeholders})
            ORDER BY created_at ASC
            """,
            complaint_ids,
        )

        reply_rows = cur.fetchall()
        replies_by_cid = {}
        reply_ids = []
        for rid, cid, msg, auser, rcreated in reply_rows:
            replies_by_cid.setdefault(cid, []).append({
                "id": rid,
                "message": msg,
                "admin_username": auser,
                "created_at": (rcreated.strftime('%Y-%m-%d %H:%M') if hasattr(rcreated, 'strftime') else str(rcreated)),
                "images": [],
            })
            reply_ids.append(rid)

        # Fetch images for replies
        if reply_ids:
            # Ensure reply images table exists before selecting
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS complaint_reply_images (
                  id INT AUTO_INCREMENT PRIMARY KEY,
                  reply_id INT NOT NULL,
                  filename VARCHAR(255) NOT NULL,
                  created_at DATETIME NOT NULL,
                  INDEX idx_reply_id (reply_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            rph = ",".join(["%s"] * len(reply_ids))
            cur.execute(
                f"SELECT reply_id, filename FROM complaint_reply_images WHERE reply_id IN ({rph})",
                reply_ids,
            )

            rimg_rows = cur.fetchall()
            images_by_rid = {}
            for rid, fname in rimg_rows:
                images_by_rid.setdefault(rid, []).append(fname)
            # Attach images to replies
            for cid, rlist in replies_by_cid.items():
                for r in rlist:
                    r["images"] = images_by_rid.get(r["id"], [])

        # Attach replies to complaints
        for c in complaints:
            c["replies"] = replies_by_cid.get(c["id"], [])

    cur.close()
    return render_template("user/reports.html", complaints=complaints)

@app.route("/user/complaints/<int:complaint_id>/replies")
def user_complaint_replies(complaint_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    try:
        cur = mysql.connection.cursor()
        # Verify ownership
        cur.execute("SELECT user_id FROM complaints WHERE id=%s", (complaint_id,))
        row = cur.fetchone()
        if not row or int(row[0]) != int(user_id):
            cur.close()
            return jsonify({"success": False, "error": "Forbidden"}), 403

        # Ensure tables exist
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS complaint_replies (
              id INT AUTO_INCREMENT PRIMARY KEY,
              complaint_id INT NOT NULL,
              message TEXT NOT NULL,
              admin_username VARCHAR(100),
              created_at DATETIME NOT NULL,
              INDEX idx_complaint_id (complaint_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS complaint_reply_images (
              id INT AUTO_INCREMENT PRIMARY KEY,
              reply_id INT NOT NULL,
              filename VARCHAR(255) NOT NULL,
              created_at DATETIME NOT NULL,
              INDEX idx_reply_id (reply_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )

        cur.execute(
            """
            SELECT id, message, admin_username, created_at
            FROM complaint_replies
            WHERE complaint_id=%s
            ORDER BY created_at ASC
            """,
            (complaint_id,)
        )
        reply_rows = cur.fetchall()
        replies = []
        reply_ids = []
        for rid, msg, auser, rcreated in reply_rows:
            replies.append({
                "id": rid,
                "message": msg,
                "admin_username": auser,
                "created_at": (rcreated.strftime('%Y-%m-%d %H:%M') if hasattr(rcreated, 'strftime') else str(rcreated)),
                "images": [],
            })
            reply_ids.append(rid)

        if reply_ids:
            placeholders = ",".join(["%s"] * len(reply_ids))
            cur.execute(
                f"SELECT reply_id, filename FROM complaint_reply_images WHERE reply_id IN ({placeholders})",
                reply_ids,
            )
            rimg_rows = cur.fetchall()
            images_by_rid = {}
            for rid, fname in rimg_rows:
                images_by_rid.setdefault(rid, []).append(fname)
            for r in replies:
                r["images"] = images_by_rid.get(r["id"], [])

        cur.close()
        return jsonify({"success": True, "replies": replies})
    except Exception as e:
        try:
            cur.close()
        except Exception:
            pass
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/user/complaint", methods=["GET", "POST"])
def user_complaint():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":

        # ---------------- Form Data ----------------
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        location_text = request.form.get("location", "").strip()
        priority = request.form.get("priority", "low").lower()
        description = request.form.get("description", "").strip()
        contact = request.form.get("contact") or None
        anonymous = 1 if request.form.get("anonymous") == "1" else 0

        try:
            latitude = float(request.form.get("latitude")) if request.form.get("latitude") else None
            longitude = float(request.form.get("longitude")) if request.form.get("longitude") else None
        except ValueError:
            latitude = longitude = None

        if not title or not category:
            flash("Title, category are required.", "error")
            return redirect(url_for("user_complaint"))

        files = request.files.getlist("images")
        MAX_SIZE = 2 * 1024 * 1024  # 2MB

        for f in files:
            if not f or not f.filename:
                continue

            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            f.seek(0)  # reset pointer

            if file_size > MAX_SIZE:
                flash("Each image must be less than 2MB ❌", "error")
                return redirect(url_for("user_complaint"))
        if not files or all(not f.filename for f in files):
            flash("Please upload at least one image.", "error")
            return redirect(url_for("user_complaint"))

        # ---------------- Detection Flags ----------------
        allowed_ext = {"png", "jpg", "jpeg", "webp"}
        validated_files = []
        pothole_detected = False
        crack_detected_any = False
        total_crack_cost = 0

        # ---------------- Process Images ----------------
        for f in files:
            if not f.filename:
                continue

            filename = secure_filename(f.filename)
            ext = filename.rsplit(".", 1)[-1].lower()
            if ext not in allowed_ext:
                continue

            try:
                # Read image ONCE
                image_bytes = f.read()
                img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)

                if img is None:
                    raise ValueError("Invalid image file")

                # -------- Crack Detection (original image) --------
                crack_result = crack_detector.detect_crack_from_image(img)
                crack_detected = crack_result.get("detected", False)
                crack_detected_any |= crack_detected
                crack_count = crack_result.get("count", 0)
                crack_cost = crack_result.get("total_cost", 0)
                total_crack_cost += crack_cost

                # -------- Pothole Detection (original image) --------
                pothole_result = pothole_detector.detect_pothole_from_image(img)
                pothole_current = pothole_result.get("detected", False)
                pothole_detected |= pothole_current

                boxes = []
                pothole_cost = 0
                if pothole_current:
                    boxes = pothole_detector.get_boxes(pothole_result["detections"])
                    pothole_cost = pothole_detector.estimate_cost(boxes, image_shape=img.shape)

                # -------- Draw Results (SAFE COPY) --------
                img_draw = img.copy()

                if pothole_current:
                    img_draw = pothole_detector.draw_boxes(img_draw, boxes)

                if crack_result["detected"]:
                    img_draw = crack_detector.draw_crack_lines(
                        img_draw,
                        crack_result["boxes"],
                        crack_result["results"]
                    )
                    crack_boxes=crack_detector.get_boxes_crack(crack_result["boxes"])

                # Encode processed image
                success, encoded = cv2.imencode(".jpg", img_draw)
                if not success:
                    raise ValueError("Image encoding failed")
                total_cost=pothole_cost+crack_cost
                validated_files.append({
                    "original": image_bytes,
                    "processed": encoded.tobytes(),
                    "boxes_pothole": boxes,
                    "boxes_crack":crack_boxes,
                    "count": pothole_result.get("count", 0),
                    "cost": pothole_cost,
                    "crack_count": crack_count,
                    "crack_cost": crack_cost,
                    "ext": ext,
                    "total_cost":total_cost
                })
                print(crack_cost)
                print(crack_boxes)
            except Exception as e:
                flash("Invalid image uploaded. Please upload a valid road image.", "error")
                return redirect(url_for("user_complaint"))

        # ---------------- Validation ----------------
        if not pothole_detected and not crack_detected_any:
            flash("No potholes or cracks detected in uploaded images.", "warning")
            return redirect(url_for("user_complaint"))

        # ---------------- Database Insert ----------------
        try:
            cur = mysql.connection.cursor()

            cur.execute("""
                INSERT INTO complaints
                (user_id, title, category, location_text, priority,
                 description, contact, anonymous, latitude, longitude,
                 status, created_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'New',NOW())
            """, (
                user_id, title, category, location_text, priority,
                description, contact, anonymous, latitude, longitude
            ))

            complaint_id = cur.lastrowid

            upload_dir = os.path.join(
                app.root_path, "static", "uploads",
                "complaints", str(complaint_id)
            )
            os.makedirs(upload_dir, exist_ok=True)

            for i, file_data in enumerate(validated_files[:6], start=1):

                # Save original
                original_name = f"original_{i}.{file_data['ext']}"
                with open(os.path.join(upload_dir, original_name), "wb") as f:
                    f.write(file_data["original"])

                cur.execute(
                    "INSERT INTO complaint_images (complaint_id, filename) VALUES (%s,%s)",
                    (complaint_id, original_name)
                )

                # Save processed
                processed_name = f"processed_{i}.jpg"
                with open(os.path.join(upload_dir, processed_name), "wb") as f:
                    f.write(file_data["processed"])

                cur.execute("""
                    INSERT INTO processed_images
                    (user_id, complaint_id, filepath, detection_pothole, detection_crack,
                    pothole_count, crack_count, pothole_estimate_cost, crack_estimate_cost,
                    total_estimate_cost)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    user_id,
                    complaint_id,
                    f"uploads/complaints/{complaint_id}/{processed_name}",
                    str(file_data["boxes_pothole"]),  
                          str(file_data["boxes_crack"]),   
                          file_data["count"],               
                          file_data["crack_count"],         
                          file_data["cost"],                
                          file_data["crack_cost"],          
                          file_data["total_cost"]
                      ))

            mysql.connection.commit()
            cur.close()

            msg = []
            if pothole_detected:
                msg.append("potholes")
            if crack_detected_any:
                msg.append("cracks")

            flash(f"Complaint submitted successfully with detected {' and '.join(msg)}.", "success")
            return redirect(url_for("user_complaint"))

        except Exception as e:
            mysql.connection.rollback()
            cur.close()
            flash(f"Database error: {str(e)}", "error")
            return redirect(url_for("user_complaint"))

    return render_template("user/complaint.html")



# @app.route("/user/complaint", methods=["GET", "POST"])
# def user_complaint():
#     user_id = session.get("user_id")
#     if not user_id:
#         flash("Please login to continue.", "error")
#         return redirect(url_for("login"))

#     if request.method == "POST":
#         title = request.form.get("title", "").strip()
#         category = request.form.get("category", "").strip()
#         location_text = request.form.get("location", "").strip()
#         priority = request.form.get("priority", "low").strip().lower()
#         description = request.form.get("description", "").strip()
#         contact = request.form.get("contact") or None
#         anonymous = 1 if request.form.get("anonymous") == "1" else 0

#         latitude = request.form.get("latitude")
#         longitude = request.form.get("longitude")

#         try:
#             latitude = float(latitude) if latitude else None
#             longitude = float(longitude) if longitude else None
#         except ValueError:
#             latitude = longitude = None

#         if not title or not category or not description:
#             flash("Title, category and description are required.", "error")
#             return redirect(url_for("user_complaint"))

#         files = request.files.getlist("images")
#         if not files or all(not f.filename for f in files):
#             flash("Please upload at least one image.", "error")
#             return redirect(url_for("user_complaint"))

#         allowed_ext = {"png", "jpg", "jpeg", "webp"}
#         validated_files = []
#         pothole_detected = False
#         crack_detected_any = False             
#         total_crack_cost = 0

#         for f in files:
#             if not f.filename:
#                 continue

#             filename = secure_filename(f.filename)
#             ext = filename.rsplit(".", 1)[-1].lower()
#             if ext not in allowed_ext:
#                 continue

#             try:
#                 image_bytes = f.read()
#                 result = pothole_detector.detect_pothole_from_bytes(image_bytes)

#                 if result["detected"]:
#                     pothole_detected = True
#                     boxes = pothole_detector.get_boxes(result["detections"])
#                     processed_image = pothole_detector.draw_boxes(image_bytes, boxes)
#                     cost = pothole_detector.estimate_cost(boxes)
#                 else:
#                     boxes = []
#                     processed_image = None
#                     cost = 0

#                 crack_result = crack_detector.detect_crack_from_bytes(image_bytes)

#                 crack_processed_image = None

#                 crack_detected = crack_result["detected"]
#                 crack_count = crack_result["count"]
#                 crack_cost = crack_result["fixed_cost"]

#                 if crack_detected:
#                     crack_detected_any = True
#                     total_crack_cost += crack_cost

#                     crack_processed_image = crack_detector.draw_segmentation(
#                         crack_result["image"],
#                         crack_result["results"]
#                     )

#                 if processed_image:
#                     img_np = cv2.imdecode(
#                     np.frombuffer(processed_image, np.uint8),
#                     cv2.IMREAD_COLOR
#                     )
#                 else:
#                     img_np = cv2.imdecode(
#                         np.frombuffer(image_bytes, np.uint8),
#                         cv2.IMREAD_COLOR
#                     ) 
#                 if crack_detected:
#                     img_np = crack_detector.draw_segmentation(
#                         img_np,
#                         crack_result["results"]
#                     )  
#                 _, encoded = cv2.imencode(".jpg", img_np)
#                 processed_image = encoded.tobytes()         
#                 validated_files.append({
#                     "original": image_bytes,
#                     "processed": processed_image,
#                     "crack_processed": crack_processed_image,
#                     "boxes": boxes,
#                     "count": result["count"],
#                     "cost": cost,
#                     "crack_count": crack_count, 
#                     "crack_cost": crack_cost,
#                     "ext": ext
#                 })

#             except Exception as e:
#                 flash(f"Error processing image: {str(e)}", "error")
#                 return redirect(url_for("user_complaint"))

#         if not pothole_detected:
#             flash("No potholes detected in uploaded images.", "warning")
#             return redirect(url_for("user_complaint"))

#         try:
#             cur = mysql.connection.cursor()

#             # Insert complaint
#             cur.execute("""
#                 INSERT INTO complaints
#                 (user_id, title, category, location_text, priority, description,
#                  contact, anonymous, latitude, longitude, status, created_at)
#                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'New',NOW())
#             """, (
#                 user_id, title, category, location_text, priority,
#                 description, contact, anonymous, latitude, longitude
#             ))

#             complaint_id = cur.lastrowid

#             upload_dir = os.path.join(
#                 app.root_path, "static", "uploads", "complaints", str(complaint_id)
#             )
#             os.makedirs(upload_dir, exist_ok=True)

#             for i, file_data in enumerate(validated_files[:6], start=1):
#                 # Save original image
#                 original_name = f"original_{i}.{file_data['ext']}"
#                 original_path = os.path.join(upload_dir, original_name)
#                 with open(original_path, "wb") as f:
#                     f.write(file_data["original"])

#                 cur.execute(
#                     "INSERT INTO complaint_images (complaint_id, filename) VALUES (%s,%s)",
#                     (complaint_id, original_name)
#                 )

#                 # Save processed image
#                 if file_data["processed"]:
#                     processed_name = f"processed_{i}.jpg"
#                     processed_path = os.path.join(upload_dir, processed_name)
#                     with open(processed_path, "wb") as f:
#                         f.write(file_data["processed"])

#                     cur.execute("""
#                         INSERT INTO processed_images
#                         (user_id, complaint_id, filepath, detection, count, estimate_cost)
#                         VALUES (%s,%s,%s,%s,%s,%s)
#                     """, (
#                         user_id,
#                         complaint_id,
#                         f"uploads/complaints/{complaint_id}/{processed_name}",
#                         str(file_data["boxes"]),
#                         file_data["count"],
#                         file_data["cost"]
#                     ))

#             mysql.connection.commit()
#             cur.close()

#             flash("Complaint submitted successfully with pothole detection.", "success")
#             return redirect(url_for("user_complaint"))

#         except Exception as e:
#             mysql.connection.rollback()
#             cur.close()
#             flash(f"Database error: {str(e)}", "error")
#             return redirect(url_for("user_complaint"))

#     return render_template("user/complaint.html")


# @app.route("/user/complaint", methods=["GET", "POST"])
# def user_complaint():
#     user_id = session.get("user_id")
#     if not user_id:
#         flash("Please login to continue.", "error")
#         return redirect(url_for("login"))

#     if request.method == "POST":
#         title = request.form.get("title", "").strip()
#         category = request.form.get("category", "").strip()
#         location_text = request.form.get("location", "").strip()
#         priority = request.form.get("priority", "low").strip().lower() or "low"
#         description = request.form.get("description", "").strip()
#         contact = request.form.get("contact", "").strip() or None
#         anonymous = 1 if request.form.get("anonymous") == "1" else 0
#         lat_raw = request.form.get("latitude")
#         lng_raw = request.form.get("longitude")
#         try:
#             latitude = float(lat_raw) if lat_raw not in (None, "") else None
#         except ValueError:
#             latitude = None
#         try:
#             longitude = float(lng_raw) if lng_raw not in (None, "") else None
#         except ValueError:
#             longitude = None

#         if not title or not category or not description:
#             flash("Title, category and description are required.", "error")
#             return redirect(url_for("user_complaint"))

#         try:
#             cur = mysql.connection.cursor()
#             insert_sql = (
#                 """
#                 INSERT INTO complaints (user_id, title, category, location_text, priority, description, contact, anonymous, latitude, longitude, status, created_at)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
#                 """
#             )
#             cur.execute(insert_sql, (user_id, title, category, location_text, priority, description, contact, anonymous, latitude, longitude, "New"))

#             complaint_id = cur.lastrowid

#             files = request.files.getlist("images")
#             allowed_ext = {"png", "jpg", "jpeg", "gif", "webp"}
#             upload_count = 0
#             if files:
#                 upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'complaints', str(complaint_id))
#                 os.makedirs(upload_dir, exist_ok=True)
#                 for f in files:
#                     if not f or not f.filename:
#                         continue
#                     if upload_count >= 6:
#                         break
#                     filename = secure_filename(f.filename)
#                     ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
#                     if ext not in allowed_ext:
#                         continue
#                     save_name = f"image_{upload_count+1}.{ext}"
#                     save_path = os.path.join(upload_dir, save_name)
#                     f.save(save_path)
#                     cur.execute(
#                         "INSERT INTO complaint_images (complaint_id, filename) VALUES (%s, %s)",
#                         (complaint_id, save_name)
#                     )
#                     upload_count += 1

#             mysql.connection.commit()
#             cur.close()
#             flash("Complaint submitted successfully.", "success")
#             return redirect(url_for("user_complaint"))
#         except Exception as e:
#             mysql.connection.rollback()
#             try:
#                 cur.close()
#             except Exception:
#                 pass
#             flash(f"Failed to submit complaint. Please try again. Error: {str(e)}", "error")
#             return redirect(url_for("user_complaint"))

#     return render_template("user/complaint.html")

@app.route("/user/settings")
def user_settings():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))
    return render_template("user/settings.html")

@app.route("/user/users")
def user_users():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))
    return render_template("user/users.html")

@app.route("/user/profile", methods=["GET", "POST"])
def user_profile():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        organization = request.form.get("organization", "").strip() or None

        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")
        current_password = request.form.get("current_password", "")
        avatar_file = request.files.get("avatar")

        if not first_name or not last_name:
            flash("First name and last name are required.", "error")
            return redirect(url_for("user_profile"))

        try:
            cur = mysql.connection.cursor()
            update_sql = (
                "UPDATE users SET first_name=%s, last_name=%s, organization=%s WHERE id=%s"
            )
            cur.execute(update_sql, (first_name, last_name, organization, user_id))

            if new_password:
                # Require current password
                if not current_password:
                    mysql.connection.rollback()
                    cur.close()
                    flash("Current password is required to change the password.", "error")
                    return redirect(url_for("user_profile"))

                # Verify current password against stored hash
                cur.execute("SELECT password_hash FROM users WHERE id=%s", (user_id,))
                row_pwd = cur.fetchone()
                if not row_pwd or not check_password_hash(row_pwd[0], current_password):
                    mysql.connection.rollback()
                    cur.close()
                    flash("Current password is incorrect.", "error")
                    return redirect(url_for("user_profile"))

                if new_password != confirm_password:
                    mysql.connection.rollback()
                    cur.close()
                    flash("Passwords do not match.", "error")
                    return redirect(url_for("user_profile"))

                pwd_hash = generate_password_hash(new_password)
                cur.execute("UPDATE users SET password_hash=%s WHERE id=%s", (pwd_hash, user_id))

            if avatar_file and avatar_file.filename:
                filename = secure_filename(avatar_file.filename)
                ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
                if ext not in {"png", "jpg", "jpeg", "gif", "webp"}:
                    mysql.connection.rollback()
                    cur.close()
                    flash("Only image files (png, jpg, jpeg, gif, webp) are allowed.", "error")
                    return redirect(url_for("user_profile"))
                upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'users', str(user_id))
                os.makedirs(upload_dir, exist_ok=True)
                save_name = f"avatar.{ext}"
                save_path = os.path.join(upload_dir, save_name)
                avatar_file.save(save_path)
                cur.execute("UPDATE users SET avatar=%s WHERE id=%s", (save_name, user_id))

            mysql.connection.commit()
            cur.close()

            # Update session display values
            session["user_name"] = f"{first_name} {last_name}"
            if session.get("user_email") is None:
                session["user_email"] = ""

            flash("Profile updated successfully.", "success")
        except Exception:
            mysql.connection.rollback()
            try:
                cur.close()
            except Exception:
                pass
            flash("Failed to update profile. Please try again.", "error")
        return redirect(url_for("user_profile"))

    # GET: fetch current user details
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT first_name, last_name, email, organization, avatar FROM users WHERE id=%s",
        (user_id,)
    )
    row = cur.fetchone()
    cur.close()

    if not row:
        flash("User not found.", "error")
        return redirect(url_for("logout"))

    user = {
        "first_name": row[0],
        "last_name": row[1],
        "email": row[2],
        "organization": row[3],
        "avatar": row[4] if len(row) > 4 else None,
    }

    user_avatar_url = _user_avatar_url(user_id, user.get("avatar"))
    return render_template("user/profile.html", user=user, user_avatar_url=user_avatar_url)

@app.route("/admin")
def admin_index():
    return redirect(url_for("admin_login"))

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        if session.get("is_admin"):
            return redirect(url_for("admin_dashboard"))
        return render_template("AdminLogin.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if username == "admin" and password == "super":
        session.clear()
        session["is_admin"] = True
        session["admin_username"] = "admin"
        return redirect(url_for("admin_dashboard"))

    flash("Invalid admin credentials.", "error")
    return render_template("AdminLogin.html"), 401

def _require_admin():
    if not session.get("is_admin"):
        flash("Please login as admin to continue.", "error")
        return False
    return True

@app.route("/admin/dashboard")
def admin_dashboard():
    if not _require_admin():
        return redirect(url_for("admin_login"))

    admin_username = session.get("admin_username", "admin")

    cur = mysql.connection.cursor()

    # -------------------------
    # 1) Total Users
    # -------------------------
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0] or 0

    # -------------------------
    # 2) Active Today (Runtime)
    # NOTE: Your users table doesn't have last_login currently.
    # So we count users created today as "Active Today".
    # -------------------------
    cur.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) = CURDATE()")
    active_today = cur.fetchone()[0] or 0

    # -------------------------
    # 3) Total Reports = Total Complaints
    # -------------------------
    cur.execute("SELECT COUNT(*) FROM complaints")
    total_reports = cur.fetchone()[0] or 0

    # -------------------------
    # 4) System Alerts
    # Example: Complaints still NEW
    # -------------------------
    cur.execute("SELECT COUNT(*) FROM complaints WHERE status='New'")
    system_alerts = cur.fetchone()[0] or 0

    # -------------------------
    # 5) Latest Users (Last 5)
    # -------------------------
    cur.execute("""
        SELECT first_name, last_name, email, user_type, created_at
        FROM users
        ORDER BY created_at DESC
        LIMIT 5
    """)
    rows = cur.fetchall()

    latest_users = []
    for r in rows:
        full_name = f"{r[0]} {r[1]}".strip()
        latest_users.append({
            "username": full_name if full_name else "User",
            "email": r[2],
            "status": "active",  # default active (since no status column)
            "created_at": r[4].strftime("%d %b %Y") if r[4] else "recently"
        })

    # -------------------------
    # 6) Latest Logins
    # Since last_login column is not present, show last registered users as activity
    # -------------------------
    latest_logins = []
    for u in latest_users:
        latest_logins.append({
            "username": u["username"],
            "email": u["email"],
            "last_login": u["created_at"]
        })

    # -------------------------
    # 7) Recent Reports (Last 5 Complaints)
    # -------------------------
    cur.execute("""
        SELECT title, created_at
        FROM complaints
        ORDER BY created_at DESC
        LIMIT 5
    """)
    report_rows = cur.fetchall()

    recent_reports = []
    for r in report_rows:
        recent_reports.append({
            "title": r[0] or "Complaint Report",
            "created_at": r[1].strftime("%d %b %Y %I:%M %p") if r[1] else "recently"
        })

    cur.close()

    # Optional progress bars (UI only)
    total_users_progress = 72
    reports_progress = 58

    return render_template(
        "admin/dashboard.html",
        admin_username=admin_username,
        admin_avatar_url=_admin_avatar_url(),

        total_users=total_users,
        active_today=active_today,
        total_reports=total_reports,
        system_alerts=system_alerts,

        latest_users=latest_users,
        latest_logins=latest_logins,
        recent_reports=recent_reports,

        total_users_progress=total_users_progress,
        reports_progress=reports_progress
    )


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("admin_login"))

# ---- Admin section placeholders for sidebar links ----
@app.route("/admin/users")
def admin_users():
    if not _require_admin():
        return redirect(url_for("admin_login"))

    cur = mysql.connection.cursor()
    # Detect status column if present
    cur.execute(
        """
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'users' AND COLUMN_NAME IN ('is_active','status','active')
        LIMIT 1
        """
    )
    col = cur.fetchone()
    status_col = col[0] if col else None

    if status_col:
        cur.execute(
            f"""
            SELECT id, first_name, last_name, email, organization, user_type, created_at, {status_col}
            FROM users
            ORDER BY created_at DESC
            """
        )
    else:
        cur.execute(
            """
            SELECT id, first_name, last_name, email, organization, user_type, created_at
            FROM users
            ORDER BY created_at DESC
            """
        )
    rows = cur.fetchall()
    cur.close()

    users = []
    for r in rows:
        u = {
            "id": r[0],
            "first_name": r[1],
            "last_name": r[2],
            "email": r[3],
            "organization": r[4],
            "user_type": r[5],
            "created_at": r[6],
        }
        if status_col:
            raw = r[7]
            # Normalize raw status into 'Active'/'Inactive'
            if isinstance(raw, (int, bool)):
                u["status"] = "Active" if int(raw) == 1 else "Inactive"
            elif isinstance(raw, str):
                u["status"] = "Active" if raw.strip().lower() in ("active","1","true","yes") else "Inactive"
            else:
                u["status"] = "Inactive"
        else:
            u["status"] = "Active"
        users.append(u)

    return render_template(
        "admin/users.html",
        admin_username=session.get("admin_username", "admin"),
        admin_avatar_url=_admin_avatar_url(),
        users=users,
    )

@app.route("/admin/users/export")
def admin_users_export():
    if not _require_admin():
        return redirect(url_for("admin_login"))

    cur = mysql.connection.cursor()
    # Detect status column if present
    cur.execute(
        """
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'users' AND COLUMN_NAME IN ('is_active','status','active')
        LIMIT 1
        """
    )
    col = cur.fetchone()
    status_col = col[0] if col else None

    if status_col:
        cur.execute(
            f"""
            SELECT id, first_name, last_name, email, organization, user_type, created_at, {status_col}
            FROM users
            ORDER BY created_at DESC
            """
        )
    else:
        cur.execute(
            """
            SELECT id, first_name, last_name, email, organization, user_type, created_at
            FROM users
            ORDER BY created_at DESC
            """
        )
    rows = cur.fetchall()
    cur.close()

    # Build CSV
    output = io.StringIO()
    writer = csv.writer(output)
    headers = ["ID", "First Name", "Last Name", "Email", "Organization", "User Type", "Created At", "Status"]
    writer.writerow(headers)

    for r in rows:
        status_str = "Active"
        if status_col:
            raw = r[7]
            if isinstance(raw, (int, bool)):
                status_str = "Active" if int(raw) == 1 else "Inactive"
            elif isinstance(raw, str):
                status_str = "Active" if raw.strip().lower() in ("active","1","true","yes") else "Inactive"
            else:
                status_str = "Inactive"
        writer.writerow([r[0], r[1], r[2], r[3], r[4], r[5], r[6], status_str])

    csv_data = output.getvalue()
    output.close()

    from flask import Response
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=users_export.csv"
        }
    )


@app.route("/admin/reports")
def admin_reports():
    if not _require_admin():
        return redirect(url_for("admin_login"))

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT c.id, c.user_id, c.title, c.category, c.location_text,
               c.priority, c.status, c.created_at,
               c.description, c.contact, c.latitude, c.longitude,
               u.first_name, u.last_name, u.email
        FROM complaints c
        JOIN users u ON u.id = c.user_id
        ORDER BY c.created_at DESC
    """)
    rows = cur.fetchall()

    complaints = []
    complaint_ids = []

    for r in rows:
        complaints.append({
            "id": r[0],
            "user_id": r[1],
            "title": r[2],
            "category": r[3],
            "location_text": r[4],
            "priority": r[5],
            "status": r[6] or "New",
            "created_at": r[7],
            "description": r[8],
            "contact": r[9],
            "latitude": r[10],
            "longitude": r[11],
            "user_name": f"{r[12]} {r[13]}",
            "user_email": r[14],
            "images": [],
            "processed_images": []
        })
        complaint_ids.append(r[0])

    # ---------------- Complaint Images ----------------
    if complaint_ids:
        placeholders = ",".join(["%s"] * len(complaint_ids))
        cur.execute(
            f"""
            SELECT complaint_id, filename
            FROM complaint_images
            WHERE complaint_id IN ({placeholders})
            """,
            complaint_ids
        )
        img_rows = cur.fetchall()

        images_by_cid = {}
        for cid, fname in img_rows:
            images_by_cid.setdefault(cid, []).append(fname)

        for c in complaints:
            c["images"] = images_by_cid.get(c["id"], [])

    # ---------------- Processed Images (Potholes + Cracks) ----------------
    if complaint_ids:
        placeholders = ",".join(["%s"] * len(complaint_ids))
        cur.execute(
            f"""
            SELECT id, complaint_id, filepath,
                   detection_pothole, detection_crack,
                   pothole_count, pothole_estimate_cost,
                   crack_count, crack_estimate_cost,
                   total_estimate_cost
            FROM processed_images
            WHERE complaint_id IN ({placeholders})
            """,
            complaint_ids
        )
        proc_rows = cur.fetchall()

        # Recalculate stored costs with current calibration so old records also reflect updated pricing.
        # Costs shown in reports come directly from the DB (processed_images.*_estimate_cost).
        try:
            import ast

            def _safe_parse_boxes(val):
                if val is None:
                    return []
                if isinstance(val, (list, tuple)):
                    return list(val)
                if isinstance(val, (bytes, bytearray)):
                    try:
                        val = val.decode("utf-8", errors="ignore")
                    except Exception:
                        return []
                if not isinstance(val, str):
                    return []
                s = val.strip()
                if not s:
                    return []
                try:
                    parsed = ast.literal_eval(s)
                    if isinstance(parsed, (list, tuple)):
                        return list(parsed)
                except Exception:
                    return []
                return []

            def _load_image_shape_from_filepath(fp):
                if not fp:
                    return None
                try:
                    full_path = os.path.join(app.root_path, "static", fp.replace("/", os.sep))
                    im = cv2.imread(full_path)
                    if im is None:
                        return None
                    return im.shape
                except Exception:
                    return None

            updated_any = False
            for (
                pid,
                cid,
                filepath,
                det_pothole,
                det_crack,
                pothole_count,
                pothole_cost,
                crack_count,
                crack_cost,
                total_cost,
            ) in proc_rows:
                try:
                    pothole_count_i = int(pothole_count or 0)
                    crack_count_i = int(crack_count or 0)
                    pothole_cost_i = int(pothole_cost or 0)
                    crack_cost_i = int(crack_cost or 0)
                    total_cost_i = int(total_cost or 0)
                except Exception:
                    continue

                # Recalculate if below new floor (₹20k per detected item)
                needs_recalc = False
                if pothole_count_i > 0 and pothole_cost_i < (20000 * pothole_count_i):
                    needs_recalc = True
                if crack_count_i > 0 and crack_cost_i < (20000 * crack_count_i):
                    needs_recalc = True

                if not needs_recalc:
                    continue

                shape = _load_image_shape_from_filepath(filepath)
                img_h = int(shape[0]) if shape and len(shape) >= 2 else None

                new_pothole_cost = pothole_cost_i
                new_crack_cost = crack_cost_i

                if pothole_count_i > 0:
                    pothole_boxes = _safe_parse_boxes(det_pothole)
                    new_pothole_cost = int(pothole_detector.estimate_cost(pothole_boxes, image_shape=shape) or 0)

                if crack_count_i > 0:
                    crack_boxes = _safe_parse_boxes(det_crack)
                    if img_h and crack_boxes:
                        tmp_total = 0
                        for b in crack_boxes:
                            try:
                                y1 = int(b.get("y1"))
                                y2 = int(b.get("y2"))
                            except Exception:
                                continue
                            height = max(1, y2 - y1)
                            severity = height / float(img_h)
                            cst = int(crack_detector.base_rate + (severity * crack_detector.severity_multiplier))
                            if cst < int(getattr(crack_detector, "min_cost_per_crack", 20000)):
                                cst = int(getattr(crack_detector, "min_cost_per_crack", 20000))
                            if cst > int(getattr(crack_detector, "max_cost_per_crack", 150000)):
                                cst = int(getattr(crack_detector, "max_cost_per_crack", 150000))
                            tmp_total += cst
                        new_crack_cost = int(tmp_total)
                    else:
                        # Fallback: still apply minimum per crack
                        new_crack_cost = max(crack_cost_i, 20000 * crack_count_i)

                new_total_cost = int(new_pothole_cost + new_crack_cost)

                if (
                    new_pothole_cost != pothole_cost_i
                    or new_crack_cost != crack_cost_i
                    or new_total_cost != total_cost_i
                ):
                    cur.execute(
                        """
                        UPDATE processed_images
                        SET pothole_estimate_cost=%s,
                            crack_estimate_cost=%s,
                            total_estimate_cost=%s
                        WHERE id=%s
                        """,
                        (new_pothole_cost, new_crack_cost, new_total_cost, pid),
                    )
                    updated_any = True

            if updated_any:
                mysql.connection.commit()
                cur.execute(
                    f"""
                    SELECT id, complaint_id, filepath,
                           detection_pothole, detection_crack,
                           pothole_count, pothole_estimate_cost,
                           crack_count, crack_estimate_cost,
                           total_estimate_cost
                    FROM processed_images
                    WHERE complaint_id IN ({placeholders})
                    """,
                    complaint_ids,
                )
                proc_rows = cur.fetchall()
        except Exception:
            pass

        processed_by_cid = {}
        for (
            _pid,
            cid,
            filepath,
            _det_pothole,
            _det_crack,
            pothole_count,
            pothole_cost,
            crack_count,
            crack_cost,
            total_cost,
        ) in proc_rows:
            processed_by_cid.setdefault(cid, []).append({
                "filepath": filepath,
                "pothole_count": pothole_count,
                "pothole_estimate_cost": pothole_cost,
                "crack_count": crack_count,
                "crack_estimate_cost": crack_cost,
                "total_estimate_cost": total_cost
            })

        for c in complaints:
            c["processed_images"] = processed_by_cid.get(c["id"], [])

    cur.close()

    return render_template(
        "admin/reports.html",
        admin_username=session.get("admin_username", "admin"),
        admin_avatar_url=_admin_avatar_url(),
        complaints=complaints
    )



# @app.route("/admin/reports")
# def admin_reports():
#     if not _require_admin():
#         return redirect(url_for("admin_login"))
#     # Fetch all complaints with user info
#     cur = mysql.connection.cursor()
#     cur.execute(
#         """
#         SELECT c.id, c.user_id, c.title, c.category, c.location_text, c.priority, c.status, c.created_at,
#                c.description, c.contact, c.latitude, c.longitude,
#                u.first_name, u.last_name, u.email
#         FROM complaints c
#         JOIN users u ON u.id = c.user_id
#         ORDER BY c.created_at DESC
#         """
#     )
#     rows = cur.fetchall()

#     complaints = []
#     complaint_ids = []
#     for r in rows:
#         c = {
#             "id": r[0],
#             "user_id": r[1],
#             "title": r[2],
#             "category": r[3],
#             "location_text": r[4],
#             "priority": r[5],
#             "status": r[6] or "New",
#             "created_at": r[7],
#             "description": r[8],
#             "contact": r[9],
#             "latitude": r[10],
#             "longitude": r[11],
#             "user_name": f"{r[12]} {r[13]}",
#             "user_email": r[14],
#             "images": [],
#         }
#         complaints.append(c)
#         complaint_ids.append(r[0])

#     if complaint_ids:
#         placeholders = ",".join(["%s"] * len(complaint_ids))
#         cur.execute(
#             f"SELECT complaint_id, filename FROM complaint_images WHERE complaint_id IN ({placeholders})",
#             complaint_ids,
#         )
#         img_rows = cur.fetchall()
#         images_by_cid = {}
#         for cid, fname in img_rows:
#             images_by_cid.setdefault(cid, []).append(fname)
#         for c in complaints:
#             c["images"] = images_by_cid.get(c["id"], [])

#     cur.close()

#     return render_template(
#         "admin/reports.html",
#         admin_username=session.get("admin_username", "admin"),
#         admin_avatar_url=_admin_avatar_url(),
#         complaints=complaints,
#     )

@app.route("/admin/settings")
def admin_settings():
    if not _require_admin():
        return redirect(url_for("admin_login"))
    return render_template(
        "admin/settings.html",
        admin_username=session.get("admin_username", "admin"),
        admin_avatar_url=_admin_avatar_url(),
    )

@app.route("/admin/complaints/<int:complaint_id>/reply", methods=["POST"])
def admin_complaint_reply(complaint_id):
    if not _require_admin():
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    # Support JSON and form-data submissions
    content_type = request.headers.get('Content-Type', '')
    if content_type.startswith('application/json'):
        data = request.get_json(silent=True) or {}
        message = (data.get("message") or "").strip()
        status = (data.get("status") or "").strip()
        files = []
    else:
        message = (request.form.get("message") or "").strip()
        status = (request.form.get("status") or "").strip()
        files = request.files.getlist("images") if hasattr(request, 'files') else []

    if not message:
        return jsonify({"success": False, "error": "Message is required"}), 400

    try:
        cur = mysql.connection.cursor()
        # Ensure replies tables exist
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS complaint_replies (
              id INT AUTO_INCREMENT PRIMARY KEY,
              complaint_id INT NOT NULL,
              message TEXT NOT NULL,
              admin_username VARCHAR(100),
              created_at DATETIME NOT NULL,
              INDEX idx_complaint_id (complaint_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS complaint_reply_images (
              id INT AUTO_INCREMENT PRIMARY KEY,
              reply_id INT NOT NULL,
              filename VARCHAR(255) NOT NULL,
              created_at DATETIME NOT NULL,
              INDEX idx_reply_id (reply_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )

        cur.execute(
            """
            INSERT INTO complaint_replies (complaint_id, message, admin_username, created_at)
            VALUES (%s, %s, %s, NOW())
            """,
            (complaint_id, message, session.get("admin_username", "admin"))
        )
        reply_id = cur.lastrowid

        # Save images if any
        allowed_ext = {"png", "jpg", "jpeg", "gif", "webp"}
        upload_count = 0
        if files:
            upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'replies', str(reply_id))
            os.makedirs(upload_dir, exist_ok=True)
            for f in files:
                if not f or not getattr(f, 'filename', ''):
                    continue
                if upload_count >= 6:
                    break
                filename = secure_filename(f.filename)
                ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
                if ext not in allowed_ext:
                    continue
                save_name = f"image_{upload_count+1}.{ext}"
                save_path = os.path.join(upload_dir, save_name)
                f.save(save_path)
                cur.execute(
                    "INSERT INTO complaint_reply_images (reply_id, filename, created_at) VALUES (%s, %s, NOW())",
                    (reply_id, save_name)
                )
                upload_count += 1

        if status:
            cur.execute("UPDATE complaints SET status=%s WHERE id=%s", (status, complaint_id))

        mysql.connection.commit()
        cur.close()
        return jsonify({"success": True, "reply_id": reply_id})
    except Exception as e:
        mysql.connection.rollback()
        try:
            cur.close()
        except Exception:
            pass
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/admin/complaints/<int:complaint_id>/priority", methods=["POST"])
def admin_complaint_set_priority(complaint_id):
    if not _require_admin():
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    priority = (data.get("priority") or "").strip().lower()
    if priority not in {"low", "medium", "high"}:
        return jsonify({"success": False, "error": "Invalid priority"}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM complaints WHERE id=%s", (complaint_id,))
        row = cur.fetchone()
        if not row:
            cur.close()
            return jsonify({"success": False, "error": "Complaint not found"}), 404

        cur.execute(
            "UPDATE complaints SET priority=%s WHERE id=%s",
            (priority, complaint_id),
        )
        mysql.connection.commit()
        cur.close()

        return jsonify({"success": True, "priority": priority})
    except Exception as e:
        try:
            mysql.connection.rollback()
        except Exception:
            pass
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/admin/security")
def admin_security():
    if not _require_admin():
        return redirect(url_for("admin_login"))
    flash("Security section coming soon.", "info")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/logs")
def admin_logs():
    if not _require_admin():
        return redirect(url_for("admin_login"))
    flash("System logs section coming soon.", "info")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/profile", methods=["GET", "POST"])
def admin_profile():
    if not _require_admin():
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        file = request.files.get("avatar")
        if not file or file.filename == "":
            flash("Please choose an image to upload.", "error")
        else:
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
            if ext not in {"png", "jpg", "jpeg", "gif", "webp"}:
                flash("Only image files (png, jpg, jpeg, gif, webp) are allowed.", "error")
            else:
                upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'admin')
                os.makedirs(upload_dir, exist_ok=True)
                save_name = f"avatar.{ext}"
                save_path = os.path.join(upload_dir, save_name)
                file.save(save_path)
                session["admin_avatar"] = save_name
                flash("Profile image updated.", "success")

        return redirect(url_for("admin_profile"))

    return render_template(
        "admin/profile.html",
        admin_username=session.get("admin_username", "admin"),
        admin_avatar_url=_admin_avatar_url(),
    )

def _admin_avatar_url():
    fname = session.get("admin_avatar")
    if not fname:
        return None
    return url_for('static', filename=f'uploads/admin/{fname}')

def _user_avatar_url(user_id, avatar_fname):
    if not avatar_fname:
        return None
    return url_for('static', filename=f'uploads/users/{user_id}/{avatar_fname}')

@app.context_processor
def inject_user_sidebar_context():
    user_id = session.get("user_id")
    if not user_id:
        return {}
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT avatar FROM users WHERE id=%s", (user_id,))
        row = cur.fetchone()
        cur.close()
        avatar_fname = row[0] if row else None
        return {"user_avatar_url": _user_avatar_url(user_id, avatar_fname)}
    except Exception:
        try:
            cur.close()
        except Exception:
            pass
        return {}

@app.route("/dashboard")
def dashboard():
    return render_template(
        "Dashboard.html",
        user_avatar_url=session.get("user_avatar_url")
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "GET":
        return render_template("ForgotPassword.html", stage="request", email="")

    action = (request.form.get("action") or "").strip()
    email = (request.form.get("email") or "").strip().lower()

    def _gen_otp(n=6):
        import random, string
        return "".join(random.choices(string.digits, k=n))

    def _send_otp_email(to_email, code):
        try:
            import smtplib
            from email.mime.text import MIMEText

            host = app.config.get("SMTP_HOST")
            port = int(app.config.get("SMTP_PORT", 587))
            user = app.config.get("SMTP_USER")
            pwd = app.config.get("SMTP_PASSWORD")
            sender = app.config.get("SMTP_SENDER", user or "no-reply@localhost")
            debug = int(app.config.get("SMTP_DEBUG", 0))

            if not host or not user or not pwd:
                print(f"[FORGOT-PASS] OTP for {to_email}: {code} (SMTP not configured)")
                return False

            msg = MIMEText(f"Your SentryRoad password reset OTP is {code}. It expires in 5 minutes.")
            msg["Subject"] = "SentryRoad Password Reset OTP"
            msg["From"] = sender
            msg["To"] = to_email

            if port == 465:
                with smtplib.SMTP_SSL(host, port, timeout=20) as s:
                    if debug:
                        s.set_debuglevel(1)
                    s.login(user, pwd)
                    s.send_message(msg)
            else:
                with smtplib.SMTP(host, port, timeout=20) as s:
                    if debug:
                        s.set_debuglevel(1)
                    s.ehlo()
                    s.starttls()
                    s.ehlo()
                    s.login(user, pwd)
                    s.send_message(msg)

            return True

        except Exception as e:
            print("[FORGOT-PASS][EMAIL-ERROR]", str(e))
            print(f"[FORGOT-PASS] OTP for {to_email}: {code}")
            return False

    # -------------------- SEND OTP --------------------
    if action == "send_otp":
        if not email:
            flash("Please enter your email.", "error")
            return render_template("ForgotPassword.html", stage="request", email=email), 400

        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM users WHERE email=%s", (email,))
        _ = cur.fetchone()
        cur.close()

        from datetime import datetime, timedelta
        code = _gen_otp()
        session["fp_otp"] = {
            "email": email,
            "code": code,
            "exp": (datetime.utcnow() + timedelta(minutes=5)).timestamp(),
        }

        _send_otp_email(email, code)

        flash("If the email exists, an OTP has been sent.", "info")
        return render_template("ForgotPassword.html", stage="verify", email=email)

    # -------------------- RESET PASSWORD --------------------
    if action == "reset":
        otp = (request.form.get("otp") or "").strip()
        new_password = request.form.get("new_password") or ""
        confirm_password = request.form.get("confirm_password") or ""

        if not email or not otp or not new_password or not confirm_password:
            flash("All fields are required.", "error")
            return render_template("ForgotPassword.html", stage="verify", email=email), 400

        if new_password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("ForgotPassword.html", stage="verify", email=email), 400

        data = session.get("fp_otp") or {}
        from datetime import datetime

        valid = (
            data
            and data.get("email") == email
            and data.get("code") == otp
            and datetime.utcnow().timestamp() <= float(data.get("exp", 0))
        )

        if not valid:
            flash("Invalid or expired OTP.", "error")
            return render_template("ForgotPassword.html", stage="verify", email=email), 400

        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id FROM users WHERE email=%s", (email,))
            row = cur.fetchone()

            if not row:
                cur.close()
                flash("If the email exists, the password has been updated.", "info")
                return redirect(url_for("login"))

            user_id = row[0]
            pwd_hash = generate_password_hash(new_password)
            cur.execute("UPDATE users SET password_hash=%s WHERE id=%s", (pwd_hash, user_id))
            mysql.connection.commit()
            cur.close()

            session.pop("fp_otp", None)
            flash("Password updated. Please sign in with your new password.", "success")
            return redirect(url_for("login"))

        except Exception:
            try:
                mysql.connection.rollback()
                cur.close()
            except Exception:
                pass

            flash("Failed to reset password. Please try again.", "error")
            return render_template("ForgotPassword.html", stage="verify", email=email), 500

    return render_template("ForgotPassword.html", stage="request", email=email)





if __name__ == "__main__":
    app.run(debug=True)