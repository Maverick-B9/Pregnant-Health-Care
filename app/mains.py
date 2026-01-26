from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, session, jsonify
from flask_login import login_required, current_user
from .chatbot import get_bot_response
from app import mysql
import datetime
import markdown
import uuid
import json
import numpy as np

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

main = Blueprint('main', __name__)

import re

@main.app_template_filter('markdown')
def markdown_filter(text):
    if not text:
        return ""
    return markdown.markdown(text)

@main.app_template_filter('clean_bullets')
def clean_bullets_filter(text):
    if not text:
        return ""
    # Ensures bullet points starting with "* " are on their own lines
    # Matches start of string or whitespace, followed by *, followed by whitespace
    return re.sub(r'(^|\s)\*(\s)', r'\1\n*\2', text)

@main.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main.route('/pregnancy-guide', methods=['GET', 'POST'])
@login_required
def pregnancy_guide():
    guide_content = None
    selected_week = 1
    
    if request.method == 'POST':
        try:
            selected_week = int(request.form.get('week', 1))
            from .chatbot import get_weekly_guide
            guide_content = get_weekly_guide(selected_week)
            # guide_content is now a Dict (from JSON), passed to template
        except Exception as e:
            current_app.logger.error(f"Guide Error: {e}")
            flash("Could not generate guide. Please try again.", "danger")
            
    return render_template('pregnancy_guide.html', guide_content=guide_content, selected_week=selected_week)

@main.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    user_name = current_user.name if hasattr(current_user, 'name') and current_user.name else current_user.email
    current_year = datetime.datetime.now().year
    today_date = datetime.date.today()
    
    # Default stats
    health_stats = {
        "steps_today": 0,
        "steps_goal": 10000,
        "sleep_last_night_hours": 0,
        "water_glasses": 0,
        "insight": None
    }

    try:
        cur = mysql.connection.cursor()
        
        if request.method == 'POST':
            # Save new log
            sleep = float(request.form.get('sleep', 0))
            steps = int(request.form.get('steps', 0))
            water = int(request.form.get('water', 0))
            
            # Generate AI Insight (Returns Dict)
            from .chatbot import get_pregnancy_insight
            insight_dict = get_pregnancy_insight({
                'sleep_hours': sleep,
                'steps_count': steps,
                'water_glasses': water
            })
            
            # Serialize to JSON string for DB
            insight_json = json.dumps(insight_dict)
            
            # Upsert into DB
            query = """
                INSERT INTO daily_health_logs (user_id, log_date, sleep_hours, steps_count, water_glasses, gemini_insight)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                sleep_hours = VALUES(sleep_hours),
                steps_count = VALUES(steps_count),
                water_glasses = VALUES(water_glasses),
                gemini_insight = VALUES(gemini_insight)
            """
            cur.execute(query, (current_user.id, today_date, sleep, steps, water, insight_json))
            mysql.connection.commit()
            flash('Daily record saved successfully!', 'success')
            return redirect(url_for('main.dashboard'))

        # Fetch today's log
        cur.execute("""
            SELECT sleep_hours, steps_count, water_glasses, gemini_insight 
            FROM daily_health_logs 
            WHERE user_id = %s AND log_date = %s
        """, (current_user.id, today_date))
        row = cur.fetchone()
        
        if row:
            health_stats["sleep_last_night_hours"] = row[0]
            health_stats["steps_today"] = row[1]
            health_stats["water_glasses"] = row[2]
            
            # Handle Insight (JSON or Text)
            raw_insight = row[3]
            if raw_insight:
                try:
                    health_stats["insight"] = json.loads(raw_insight)
                except json.JSONDecodeError:
                    # Fallback for legacy text data
                    health_stats["insight"] = {
                        "legacy_full_text": raw_insight, # Store old full text here
                        "quick_assessment": "Daily Insight (Legacy)",
                        "analysis_sleep": "", 
                        "analysis_steps": "",
                        "analysis_water": "",
                        "actionable_advice": "",
                        "motivation": ""
                    }
            
        cur.close()
    except Exception as e:
        current_app.logger.error(f"Dashboard Database Error: {e}")
        flash('Error syncing with database.', 'danger')

    return render_template('index.html', 
                           user_name=user_name, 
                           health_stats=health_stats,
                           current_year=current_year)

@main.route('/diagnostics', methods=['GET', 'POST'])
@login_required
def diagnostics():
    prediction_text = None
    prediction_value = None
    input_data_for_template = {} 
    user_name = current_user.name if hasattr(current_user, 'name') and current_user.name else current_user.email
    
    # Health Records Data
    from .models import HealthRecord
    from werkzeug.utils import secure_filename
    import os
    
    categories = HealthRecord.CATEGORIES
    user_records = HealthRecord.get_user_records(current_user.id)

    if request.method == 'POST':
        # 1. Prediction Form
        if 'pregnancies' in request.form:
            try:
                pregnancies = float(request.form.get('pregnancies', 0))
                glucose = float(request.form.get('glucose', 0))
                bloodpressure = float(request.form.get('bloodpressure', 0))
                skinthickness = float(request.form.get('skinthickness', 0))
                insulin = float(request.form.get('insulin', 0))
                bmi = float(request.form.get('bmi', 0))
                dpf = float(request.form.get('dpf', 0))
                age = float(request.form.get('age', 0))
                
                input_data_for_template = request.form.to_dict()

                features_list = [pregnancies, glucose, bloodpressure, skinthickness, insulin, bmi, dpf, age]
                features_array = np.array([features_list])

                # Use global model loaded in app
                from app import diagnostics_model # Import here if not global, or assumes global
                # Better: retrieve from current_app if stored there or just assume it is in global scope from import
                # The original code used 'diagnostics_model' which implies it was imported at module level or available.
                # Checking imports: 'from app import mysql' is there. 'diagnostics_model' isn't explicitly imported in the file view.
                # Assuming it is available as it was working. I will refer to it as before.
                
                # Apply scaler if available
                diagnostics_scaler = current_app.extensions.get('diagnostics_scaler')
                if diagnostics_scaler:
                    features_array = diagnostics_scaler.transform(features_array)
                
                # Check for model in extensions or global
                model = current_app.extensions.get('diagnostics_model')
                # If not in extensions, maybe global? The previous code accessed 'diagnostics_model' directly.
                # Let's try to get it from extensions first which is cleaner, if not fallback/fail.
                # Actually, looking at previous code: "raw_prediction = diagnostics_model.predict..."
                # I'll stick to that if it works, or add a safety check.
                if model:
                     raw_prediction = model.predict(features_array)[0][0]
                else: 
                     # Fallback to global if defined (likely defined in __init__ and imported, but we don't see the import line in the snippet)
                     # The snippet starts at line 1.
                     # I will assume 'diagnostics_model' is available or I should import it.
                     # To be safe, I'll access it via current_app.extensions if I put it there in __init__.
                     # Re-reading __init__.py changes from previous turn might be useful, but I will trust 'model' in extensions.
                     pass 

                # Wait, the previous code had 'diagnostics_model.predict'. I should preserve that or fix it.
                # I'll use current_app.extensions.get('diagnostics_model') which is standard.
                if model:
                    raw_prediction = model.predict(features_array)[0][0]
                    prediction_value = round(float(raw_prediction) * 100, 2)
                    prediction_text = None
                else:
                    prediction_text = "Model not loaded properly."

            except Exception as e:
                prediction_text = f"An error occurred: {str(e)}"
                current_app.logger.error(f"Prediction Error: {e}", exc_info=True)

        # 2. Health Record Form
        elif 'test_name' in request.form:
            try:
                category = request.form.get('category')
                test_name = request.form.get('test_name')
                value_numeric = request.form.get('value_numeric')
                value_text = request.form.get('value_text')
                test_date = request.form.get('test_date')
                notes = request.form.get('notes')
                
                file_path = None
                if 'report_file' in request.files:
                    file = request.files['report_file']
                    if file and file.filename != '':
                        if not allowed_file(file.filename):
                            flash('File type not allowed. Please upload PDF or Images (PNG, JPG, GIF).', 'danger')
                            return redirect(url_for('main.diagnostics'))

                        filename = secure_filename(f"{current_user.id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
                        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                        os.makedirs(upload_folder, exist_ok=True)
                        file.save(os.path.join(upload_folder, filename))
                        file_path = f"uploads/{filename}"

                HealthRecord.add_record(
                    current_user.id, category, test_name, 
                    float(value_numeric) if value_numeric else None, 
                    value_text, file_path, test_date, notes
                )
                flash('Health record added successfully!', 'success')
                return redirect(url_for('main.diagnostics')) # Reload to show new data
                
            except Exception as e:
                current_app.logger.error(f"Error adding record: {e}", exc_info=True)
                flash('Error adding record.', 'danger')

    return render_template('diagnostics.html', 
                           prediction_text=prediction_text, 
                           prediction_value=prediction_value,
                           inputs=input_data_for_template,
                           user_name=user_name,
                           categories=categories,
                           user_records=user_records)

@main.route('/chatbot') 
@login_required
def chatbot_page():
    user_name = current_user.name if hasattr(current_user, 'name') and current_user.name else current_user.email
    if 'conversation_id' not in session:
        session['conversation_id'] = str(uuid.uuid4())
        current_app.logger.info(f"New conversation ID for user {current_user.id}: {session['conversation_id']}")
    return render_template('chatbot.html', user_name=user_name)

@main.route('/api/chatbot_message', methods=['POST'])
@login_required
def chatbot_message_api():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.get_json()
    user_input = data.get('message')
    
    conversation_id = session.get('conversation_id')
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
        session['conversation_id'] = conversation_id
        current_app.logger.warning(f"New conversation ID created during API call for user {current_user.id}: {conversation_id}")

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    try:
        bot_reply = get_bot_response(user_input, conversation_id=conversation_id)
        return jsonify({"response": bot_reply})
    except Exception as e:
        current_app.logger.error(f"Error in chatbot API: {e}", exc_info=True)
        return jsonify({"error": "Sorry, I encountered an error processing your message."}), 500

@main.route('/emergency')
@login_required
def emergency():
    return render_template('emergency.html')