#!/usr/bin/env python3
"""
Instagram Story Monitor Web App
Deployable on Railway with user authentication and SQL database
"""

import os
import json
import time
import subprocess
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import threading
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///instagram_monitor.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Global variable to store active monitoring sessions
active_monitors = {}

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    instagram_username = db.Column(db.String(80), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    stories = db.relationship('Story', backref='user', lazy=True, cascade='all, delete-orphan')
    viewers = db.relationship('Viewer', backref='user', lazy=True, cascade='all, delete-orphan')

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    story_date = db.Column(db.String(20), nullable=False)  # YYYY-MM-DD format
    total_views = db.Column(db.Integer, default=0)
    total_likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_checked = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    story_viewers = db.relationship('StoryViewer', backref='story', lazy=True, cascade='all, delete-orphan')

class Viewer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    total_views = db.Column(db.Integer, default=0)
    total_likes = db.Column(db.Integer, default=0)
    first_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    story_interactions = db.relationship('StoryViewer', backref='viewer', lazy=True, cascade='all, delete-orphan')

class StoryViewer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'), nullable=False)
    viewer_id = db.Column(db.Integer, db.ForeignKey('viewer.id'), nullable=False)
    has_viewed = db.Column(db.Boolean, default=False)
    has_liked = db.Column(db.Boolean, default=False)
    first_detected = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicates
    __table_args__ = (db.UniqueConstraint('story_id', 'viewer_id', name='unique_story_viewer'),)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class InstagramMonitor:
    def __init__(self, user_id, instagram_username):
        self.user_id = user_id
        self.instagram_username = instagram_username
        self.driver = None
        self.is_running = False
        self.session_id = str(uuid.uuid4())
        
    def setup_chrome(self):
        """Setup Chrome with stability options"""
        try:
            subprocess.run(["taskkill", "/f", "/im", "chrome.exe"], 
                          capture_output=True, check=False)
            time.sleep(2)
        except:
            pass
        
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--log-level=3")
        options.add_argument("--disable-logging")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-extensions")
        options.add_argument("--headless")  # Run headless for server deployment
        
        try:
            self.driver = webdriver.Chrome(options=options)
            return True
        except Exception as e:
            print(f"Chrome setup failed: {e}")
            return False
    
    def wait_for_login(self):
        """Simulate login wait - in production, implement proper OAuth"""
        try:
            self.driver.get("https://www.instagram.com/")
            time.sleep(5)
            
            # For now, return True - in production, implement proper login flow
            return True
            
        except Exception as e:
            print(f"Login error: {e}")
            return False
    
    def go_to_profile(self):
        """Go to user's Instagram profile"""
        try:
            self.driver.get(f"https://www.instagram.com/{self.instagram_username}/")
            time.sleep(3)
            
            # Look for story ring
            story_selectors = [
                "canvas[height='77'][width='77']",
                "canvas[height='56'][width='56']",
                "div[role='button'] canvas"
            ]
            
            for selector in story_selectors:
                try:
                    canvas_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for canvas in canvas_elements:
                        if canvas.is_displayed():
                            parent = canvas.find_element(By.XPATH, "..")
                            self.driver.execute_script("arguments[0].click();", parent)
                            time.sleep(3)
                            return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            print(f"Error going to profile: {e}")
            return False
    
    def get_story_data(self):
        """Get story viewers and likes"""
        try:
            # Find "Seen by X" element
            seen_by_selectors = [
                "//span[contains(text(), 'Seen by')]",
                "//button[contains(text(), 'Seen by')]",
                "//*[contains(text(), 'Seen by')]"
            ]
            
            seen_by_element = None
            for selector in seen_by_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed():
                            text = element.text.strip()
                            if 'seen by' in text.lower() and any(char.isdigit() for char in text):
                                seen_by_element = element
                                break
                    if seen_by_element:
                        break
                except:
                    continue
            
            if not seen_by_element:
                return {"viewers": [], "likes": []}
            
            # Click to see viewers
            self.driver.execute_script("arguments[0].click();", seen_by_element)
            time.sleep(3)
            
            # Extract viewers and likes
            viewers = []
            likes = []
            
            # Look for viewer elements
            viewer_selectors = [
                "a[href*='/'][role='link']",
                "a[href*='/']"
            ]
            
            for selector in viewer_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            href = element.get_attribute('href') or ''
                            text = element.text.strip()
                            
                            # Extract username from href
                            username = None
                            if href and '/p/' not in href and '/' in href:
                                parts = href.split('/')
                                for part in parts:
                                    if (part and 
                                        part not in ['www.instagram.com', 'instagram.com', 'stories', 'highlights'] and
                                        not part.startswith('http')):
                                        username = part
                                        break
                            
                            if not username and text and self.is_valid_username(text):
                                username = text
                            
                            if username and username != self.instagram_username and username not in viewers:
                                viewers.append(username)
                                
                                # Check if this viewer has liked the story
                                try:
                                    # Look for heart icon near this viewer
                                    parent = element.find_element(By.XPATH, "../..")
                                    heart_elements = parent.find_elements(By.CSS_SELECTOR, "[data-testid='heart'], .heart, [aria-label*='like'], [aria-label*='Like']")
                                    if heart_elements:
                                        likes.append(username)
                                except:
                                    pass
                except:
                    continue
            
            return {"viewers": viewers, "likes": likes}
            
        except Exception as e:
            print(f"Error getting story data: {e}")
            return {"viewers": [], "likes": []}
    
    def is_valid_username(self, text):
        """Check if text looks like a valid Instagram username"""
        if not text or len(text) < 1 or len(text) > 30:
            return False
        if not any(char.isalpha() for char in text):
            return False
        if text.isdigit() or ' ' in text:
            return False
        if text.startswith('http') or text in ['https:', 'www.', '.com']:
            return False
        return True
    
    def update_database(self, story_data):
        """Update database with story data - no duplicate counting"""
        try:
            story_date = datetime.now().strftime("%Y-%m-%d")
            
            # Get or create story record
            story = Story.query.filter_by(user_id=self.user_id, story_date=story_date).first()
            if not story:
                story = Story(user_id=self.user_id, story_date=story_date)
                db.session.add(story)
                db.session.commit()
            
            # Update story last checked time
            story.last_checked = datetime.utcnow()
            
            # Process viewers
            for viewer_username in story_data["viewers"]:
                # Get or create viewer record
                viewer = Viewer.query.filter_by(user_id=self.user_id, username=viewer_username).first()
                if not viewer:
                    viewer = Viewer(user_id=self.user_id, username=viewer_username)
                    db.session.add(viewer)
                    db.session.commit()
                
                # Update viewer last seen
                viewer.last_seen = datetime.utcnow()
                
                # Get or create story-viewer relationship (prevents duplicates)
                story_viewer = StoryViewer.query.filter_by(story_id=story.id, viewer_id=viewer.id).first()
                if not story_viewer:
                    story_viewer = StoryViewer(story_id=story.id, viewer_id=viewer.id, has_viewed=True)
                    db.session.add(story_viewer)
                    
                    # Only increment counts for NEW viewers (no duplicates)
                    viewer.total_views += 1
                else:
                    # Update existing record
                    story_viewer.has_viewed = True
                    story_viewer.last_updated = datetime.utcnow()
            
            # Process likes
            for liker_username in story_data["likes"]:
                viewer = Viewer.query.filter_by(user_id=self.user_id, username=liker_username).first()
                if viewer:
                    story_viewer = StoryViewer.query.filter_by(story_id=story.id, viewer_id=viewer.id).first()
                    if story_viewer and not story_viewer.has_liked:
                        story_viewer.has_liked = True
                        story_viewer.last_updated = datetime.utcnow()
                        
                        # Only increment like count if not already liked
                        viewer.total_likes += 1
            
            # Update story totals
            story.total_views = len(StoryViewer.query.filter_by(story_id=story.id, has_viewed=True).all())
            story.total_likes = len(StoryViewer.query.filter_by(story_id=story.id, has_liked=True).all())
            
            db.session.commit()
            
        except Exception as e:
            print(f"Database update error: {e}")
            db.session.rollback()
    
    def monitor_loop(self):
        """Main monitoring loop"""
        self.is_running = True
        
        try:
            if not self.setup_chrome():
                return
            
            if not self.wait_for_login():
                return
            
            while self.is_running:
                try:
                    if self.go_to_profile():
                        story_data = self.get_story_data()
                        if story_data["viewers"]:
                            self.update_database(story_data)
                    
                    # Wait 5 minutes before next check
                    for _ in range(300):  # 5 minutes = 300 seconds
                        if not self.is_running:
                            break
                        time.sleep(1)
                        
                except Exception as e:
                    print(f"Monitor loop error: {e}")
                    time.sleep(60)
                    
        except Exception as e:
            print(f"Monitor error: {e}")
        finally:
            self.cleanup()
    
    def stop(self):
        """Stop monitoring"""
        self.is_running = False
    
    def cleanup(self):
        """Clean shutdown"""
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        instagram_username = request.form.get('instagram_username', '')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('register'))
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            instagram_username=instagram_username
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    # Stop monitoring if active
    if current_user.id in active_monitors:
        active_monitors[current_user.id].stop()
        del active_monitors[current_user.id]
    
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's stories and analytics
    stories = Story.query.filter_by(user_id=current_user.id).order_by(Story.story_date.desc()).limit(7).all()
    viewers = Viewer.query.filter_by(user_id=current_user.id).order_by(Viewer.total_views.desc()).limit(10).all()
    
    # Check if monitoring is active
    is_monitoring = current_user.id in active_monitors
    
    return render_template('dashboard.html', 
                         stories=stories, 
                         viewers=viewers, 
                         is_monitoring=is_monitoring,
                         instagram_username=current_user.instagram_username)

@app.route('/start_monitoring', methods=['POST'])
@login_required
def start_monitoring():
    if not current_user.instagram_username:
        flash('Please set your Instagram username in profile settings')
        return redirect(url_for('profile'))
    
    if current_user.id not in active_monitors:
        monitor = InstagramMonitor(current_user.id, current_user.instagram_username)
        active_monitors[current_user.id] = monitor
        
        # Start monitoring in background thread
        thread = threading.Thread(target=monitor.monitor_loop)
        thread.daemon = True
        thread.start()
        
        flash('Monitoring started successfully!')
    else:
        flash('Monitoring is already active')
    
    return redirect(url_for('dashboard'))

@app.route('/stop_monitoring', methods=['POST'])
@login_required
def stop_monitoring():
    if current_user.id in active_monitors:
        active_monitors[current_user.id].stop()
        del active_monitors[current_user.id]
        flash('Monitoring stopped')
    else:
        flash('No active monitoring session')
    
    return redirect(url_for('dashboard'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.instagram_username = request.form['instagram_username']
        db.session.commit()
        flash('Profile updated successfully')
        return redirect(url_for('profile'))
    
    return render_template('profile.html')

@app.route('/analytics')
@login_required
def analytics():
    # Get detailed analytics
    stories = Story.query.filter_by(user_id=current_user.id).order_by(Story.story_date.desc()).all()
    viewers = Viewer.query.filter_by(user_id=current_user.id).order_by(Viewer.total_views.desc()).all()
    
    # Calculate statistics
    total_stories = len(stories)
    total_unique_viewers = len(viewers)
    total_views = sum(viewer.total_views for viewer in viewers)
    total_likes = sum(viewer.total_likes for viewer in viewers)
    
    return render_template('analytics.html',
                         stories=stories,
                         viewers=viewers,
                         total_stories=total_stories,
                         total_unique_viewers=total_unique_viewers,
                         total_views=total_views,
                         total_likes=total_likes)

@app.route('/api/stats')
@login_required
def api_stats():
    """API endpoint for real-time stats"""
    stories = Story.query.filter_by(user_id=current_user.id).order_by(Story.story_date.desc()).limit(7).all()
    
    stats = []
    for story in stories:
        stats.append({
            'date': story.story_date,
            'views': story.total_views,
            'likes': story.total_likes
        })
    
    return jsonify(stats)

# Initialize database
def create_tables():
    with app.app_context():
        db.create_all()

# Create tables on app startup (for production deployment)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Create tables on startup (for local development)
    create_tables()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 