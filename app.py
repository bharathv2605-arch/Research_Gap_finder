"""
app.py - Main Flask Application
Research Gap Finder - AI Based Research Paper Analysis System

This is the main entry point of the application.
Run this file to start the web server: python app.py
"""

import os
import json
import uuid
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify
)

# Import custom modules
from db_setup import get_connection, create_tables
from pdf_reader import extract_text
from nlp_module import preprocess_text, get_word_frequency
from keyword_extractor import (
    extract_keywords_tfidf, extract_keywords_multi,
    get_common_keywords, get_unique_keywords
)
from gap_finder import find_research_gaps, calculate_similarity

# ============================================================
# Flask Application Setup
# ============================================================
app = Flask(__name__)
app.secret_key = 'research_gap_finder_secret_key_2024'

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max file size

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ============================================================
# Route: Home / Login Page
# ============================================================
@app.route('/', methods=['GET'])
def home():
    """Redirect to login page."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('login.html')

        # Check credentials in database
        conn = get_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?',
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            # Set session variables
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')


# ============================================================
# Route: Register
# ============================================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle new user registration."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm = request.form.get('confirm_password', '').strip()

        if not username or not password:
            flash('Please fill in all fields.', 'error')
            return render_template('register.html')

        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')

        if len(password) < 4:
            flash('Password must be at least 4 characters.', 'error')
            return render_template('register.html')

        conn = get_connection()
        try:
            conn.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, password)
            )
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception:
            flash('Username already exists.', 'error')
        finally:
            conn.close()

    return render_template('register.html')


# ============================================================
# Route: Logout
# ============================================================
@app.route('/logout')
def logout():
    """Clear session and logout user."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# ============================================================
# Route: Dashboard
# ============================================================
@app.route('/dashboard')
def dashboard():
    """Show the main dashboard with uploaded papers."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Get user's uploaded papers
    conn = get_connection()
    papers = conn.execute(
        'SELECT * FROM papers WHERE user_id = ? ORDER BY upload_date DESC',
        (session['user_id'],)
    ).fetchall()

    # Get recent analysis results
    analyses = conn.execute(
        'SELECT * FROM analysis_results WHERE user_id = ? ORDER BY analysis_date DESC LIMIT 5',
        (session['user_id'],)
    ).fetchall()
    conn.close()

    return render_template(
        'dashboard.html',
        papers=papers,
        analyses=analyses,
        paper_count=len(papers)
    )


# ============================================================
# Route: Upload Papers
# ============================================================
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Handle file upload (supports multiple files)."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Check if files were uploaded
        if 'files' not in request.files:
            flash('No files selected.', 'error')
            return redirect(url_for('upload'))

        files = request.files.getlist('files')
        uploaded_count = 0

        for file in files:
            if file and file.filename and allowed_file(file.filename):
                # Generate unique filename to avoid conflicts
                original_name = file.filename
                ext = original_name.rsplit('.', 1)[1].lower()
                unique_name = f"{uuid.uuid4().hex[:8]}_{original_name}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)

                # Save file
                file.save(filepath)

                # Extract text from the file
                text_content = extract_text(filepath)

                # Save to database
                conn = get_connection()
                conn.execute(
                    '''INSERT INTO papers (user_id, filename, original_name, text_content)
                       VALUES (?, ?, ?, ?)''',
                    (session['user_id'], unique_name, original_name, text_content)
                )
                conn.commit()
                conn.close()

                uploaded_count += 1
            elif file and file.filename:
                flash(f'File "{file.filename}" has an unsupported format.', 'error')

        if uploaded_count > 0:
            flash(f'Successfully uploaded {uploaded_count} file(s)!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('No valid files were uploaded.', 'error')

    return render_template('upload.html')


# ============================================================
# Route: Delete Paper
# ============================================================
@app.route('/delete_paper/<int:paper_id>')
def delete_paper(paper_id):
    """Delete an uploaded paper."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    paper = conn.execute(
        'SELECT * FROM papers WHERE id = ? AND user_id = ?',
        (paper_id, session['user_id'])
    ).fetchone()

    if paper:
        # Delete the file from disk
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], paper['filename'])
        if os.path.exists(filepath):
            os.remove(filepath)

        # Delete from database (keywords and paper)
        conn.execute('DELETE FROM keywords WHERE paper_id = ?', (paper_id,))
        conn.execute('DELETE FROM papers WHERE id = ?', (paper_id,))
        conn.commit()
        flash('Paper deleted successfully.', 'success')
    else:
        flash('Paper not found.', 'error')

    conn.close()
    return redirect(url_for('dashboard'))


# ============================================================
# Route: Analyze Papers
# ============================================================
@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Analyze selected papers for research gaps.
    This is the main analysis endpoint.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Get selected paper IDs
    paper_ids = request.form.getlist('paper_ids')

    if not paper_ids:
        flash('Please select at least one paper to analyze.', 'error')
        return redirect(url_for('dashboard'))

    # Fetch papers from database
    conn = get_connection()
    papers = []
    for pid in paper_ids:
        paper = conn.execute(
            'SELECT * FROM papers WHERE id = ? AND user_id = ?',
            (pid, session['user_id'])
        ).fetchone()
        if paper:
            papers.append(dict(paper))

    if not papers:
        flash('No valid papers found.', 'error')
        conn.close()
        return redirect(url_for('dashboard'))

    # ---- Step 1: Preprocess text from each paper ----
    preprocessed_texts = []
    raw_texts = []
    for paper in papers:
        raw = paper.get('text_content', '') or ''
        raw_texts.append(raw)
        processed = preprocess_text(raw)
        preprocessed_texts.append(processed)
        paper['processed_text'] = processed

    # ---- Step 2: Extract keywords for each paper ----
    all_keywords = extract_keywords_multi(preprocessed_texts, top_n=15)

    # Save keywords to database
    for i, paper in enumerate(papers):
        # Clear old keywords
        conn.execute('DELETE FROM keywords WHERE paper_id = ?', (paper['id'],))

        if i < len(all_keywords):
            for keyword, score in all_keywords[i]:
                conn.execute(
                    'INSERT INTO keywords (paper_id, keyword, score) VALUES (?, ?, ?)',
                    (paper['id'], keyword, round(score, 4))
                )
            paper['keywords'] = all_keywords[i]
        else:
            paper['keywords'] = []

    # ---- Step 3: Find common and unique keywords ----
    common_keywords = get_common_keywords(all_keywords)
    unique_keywords = get_unique_keywords(all_keywords)

    for i, paper in enumerate(papers):
        if i < len(unique_keywords):
            paper['unique_keywords'] = list(unique_keywords[i])
        else:
            paper['unique_keywords'] = []

    # ---- Step 4: Get word frequencies ----
    for paper in papers:
        paper['word_freq'] = get_word_frequency(paper['processed_text'], top_n=10)

    # ---- Step 5: Run gap analysis ----
    gap_results = find_research_gaps(preprocessed_texts, all_keywords)

    # ---- Step 6: Save analysis results ----
    paper_names = json.dumps([p['original_name'] for p in papers])
    common_topics_json = json.dumps(gap_results.get('covered_topics', []))
    missing_topics_json = json.dumps(gap_results.get('missing_topics', []))
    gaps_json = json.dumps(gap_results.get('gaps', []))
    suggestions_json = json.dumps(gap_results.get('suggestions', []))

    conn.execute(
        '''INSERT INTO analysis_results
           (user_id, papers_analyzed, common_topics, missing_topics, gaps, suggestions)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (session['user_id'], paper_names, common_topics_json,
         missing_topics_json, gaps_json, suggestions_json)
    )
    conn.commit()
    conn.close()

    # ---- Render results page ----
    return render_template(
        'result.html',
        papers=papers,
        common_keywords=list(common_keywords),
        gap_results=gap_results,
        paper_count=len(papers)
    )


# ============================================================
# Route: View Analysis History
# ============================================================
@app.route('/history/<int:analysis_id>')
def view_history(analysis_id):
    """View a previous analysis result."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    analysis = conn.execute(
        'SELECT * FROM analysis_results WHERE id = ? AND user_id = ?',
        (analysis_id, session['user_id'])
    ).fetchone()
    conn.close()

    if not analysis:
        flash('Analysis not found.', 'error')
        return redirect(url_for('dashboard'))

    # Parse JSON fields
    result = {
        'papers_analyzed': json.loads(analysis['papers_analyzed']),
        'covered_topics': json.loads(analysis['common_topics']),
        'missing_topics': json.loads(analysis['missing_topics']),
        'gaps': json.loads(analysis['gaps']),
        'suggestions': json.loads(analysis['suggestions']),
        'date': analysis['analysis_date']
    }

    return render_template('history.html', result=result)


# ============================================================
# Initialize database and run the application
# ============================================================
if __name__ == '__main__':
    # Create database tables on first run
    create_tables()
    print("\n" + "=" * 55)
    print("  RESEARCH GAP FINDER")
    print("  AI Based Research Paper Analysis System")
    print("=" * 55)
    print("  Server running at: http://127.0.0.1:5000")
    print("  Default login -> username: admin | password: admin123")
    print("=" * 55 + "\n")

    # Run Flask development server
    app.run(debug=True, host='127.0.0.1', port=5000)
