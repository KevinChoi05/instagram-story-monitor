# 📸 Instagram Story Monitor

A comprehensive web application for tracking Instagram story viewers and likes with detailed analytics. Deploy on Railway with one click!

## ✨ Features

### 🔍 **Story Tracking**
- **Real-time monitoring** of Instagram stories
- **Viewer detection** - see who viewed your stories
- **Like tracking** - detect who liked your stories
- **No duplicate counting** - accurate counts per story

### 📊 **Analytics Dashboard**
- **Beautiful web interface** with modern UI
- **Interactive charts** showing performance trends
- **Engagement metrics** and insights
- **Top viewers** and activity tracking

### 👥 **Multi-User Support**
- **User registration** and secure login
- **Individual dashboards** for each user
- **Personal Instagram account linking**
- **Isolated data** per user

### 🗄️ **Data Management**
- **SQL database** for persistent storage
- **Historical data** tracking
- **Export capabilities**
- **Data privacy** and security

## 🚀 Quick Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/instagram-story-monitor)

### Manual Railway Deployment

1. **Fork this repository**
2. **Connect to Railway:**
   - Go to [Railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your forked repository

3. **Set Environment Variables:**
   ```env
   SECRET_KEY=your-super-secret-key-here
   DATABASE_URL=postgresql://user:pass@host:port/db
   ```

4. **Deploy!** 🎉

## 🖥️ Local Development

### Prerequisites
- Python 3.8+
- Chrome browser
- ChromeDriver

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/instagram-story-monitor.git
   cd instagram-story-monitor
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables:**
   ```bash
   export SECRET_KEY="your-secret-key"
   export DATABASE_URL="sqlite:///local.db"
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Open your browser:**
   ```
   http://localhost:5000
   ```

## 📱 How to Use

### 1. **Create Account**
- Register with username, email, and password
- Add your Instagram username in profile settings

### 2. **Start Monitoring**
- Click "Start Monitoring" on dashboard
- Browser will open - login to Instagram
- System automatically tracks your stories

### 3. **View Analytics**
- Real-time dashboard updates
- Detailed analytics page with charts
- Export data for further analysis

## 🛡️ Privacy & Security

### **Data Protection**
- ✅ **Encrypted passwords** using bcrypt hashing
- ✅ **Secure sessions** with Flask-Login
- ✅ **No Instagram passwords stored**
- ✅ **User data isolation**

### **Instagram Compliance**
- ✅ **No API key required** - uses web scraping
- ✅ **Respects rate limits** with delays
- ✅ **Manual login required** - no stored credentials
- ✅ **User-controlled monitoring**

## ⚙️ Technical Details

### **Architecture**
- **Backend:** Python Flask with SQLAlchemy ORM
- **Frontend:** Bootstrap 5 with responsive design
- **Database:** PostgreSQL (production) / SQLite (development)
- **Automation:** Selenium WebDriver with Chrome
- **Charts:** Chart.js for interactive visualizations

### **Key Features Implemented**
```python
# Fixed duplicate counting issue
def update_database(self, story_data):
    # Only increment counts for NEW viewers per story
    story_viewer = StoryViewer.query.filter_by(
        story_id=story.id, 
        viewer_id=viewer.id
    ).first()
    
    if not story_viewer:  # New viewer for this story
        viewer.total_views += 1  # Only count once per story
```

### **Database Schema**
- **Users:** Account management and Instagram usernames
- **Stories:** Daily story records with view/like counts
- **Viewers:** Unique viewer profiles across all stories
- **StoryViewers:** Many-to-many relationship preventing duplicates

## 🔧 Configuration

### **Environment Variables**
| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Flask session encryption key | ✅ Yes |
| `DATABASE_URL` | PostgreSQL connection string | ✅ Yes |
| `PORT` | Server port (auto-set by Railway) | ❌ No |

### **Chrome Options**
- Headless mode for server deployment
- Anti-detection measures
- Stable browser configuration
- Automatic crash recovery

## 📊 Analytics Features

### **Dashboard Metrics**
- Stories tracked count
- Unique viewers count
- Total views and likes
- Real-time monitoring status

### **Detailed Analytics**
- Story performance over time
- Engagement rate calculations
- Top viewers ranking
- Activity timeline

### **Charts & Visualizations**
- Line charts for trends
- Pie charts for engagement
- Responsive design for mobile
- Interactive hover effects

## 🚨 Important Notes

### **Instagram Limitations**
- ❌ **Cannot track view frequency** - Instagram only shows "who viewed"
- ❌ **No official API** for story viewer data
- ✅ **Can track unique viewers** per story accurately
- ✅ **Can detect likes** on stories

### **Counting Logic**
```
✅ Correct: kevinchoi284 viewed Story A = 1 view
✅ Correct: kevinchoi284 viewed Story B = 1 view (total: 2 views)
❌ Wrong: Script restart doesn't add duplicate counts
✅ Fixed: Each story-viewer combination counted only once
```

## 🐛 Troubleshooting

### **Common Issues**

1. **Chrome driver not found:**
   ```bash
   # Install ChromeDriver
   wget https://chromedriver.storage.googleapis.com/latest/chromedriver_linux64.zip
   unzip chromedriver_linux64.zip
   sudo mv chromedriver /usr/local/bin/
   ```

2. **Database connection error:**
   ```bash
   # Check DATABASE_URL format
   postgresql://user:password@host:port/database
   ```

3. **Instagram login issues:**
   - Use manual login when browser opens
   - Avoid automated login (against TOS)
   - Clear browser data if needed

## 📈 Roadmap

### **Planned Features**
- [ ] Email notifications for new viewers
- [ ] Webhook integrations
- [ ] Data export (CSV/JSON)
- [ ] Mobile app companion
- [ ] Advanced filtering options

### **Technical Improvements**
- [ ] Redis caching for performance
- [ ] Background job queue
- [ ] API endpoints for external access
- [ ] Docker containerization

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and personal use only. It complies with Instagram's public data access but users should:

- ✅ Only monitor their own Instagram accounts
- ✅ Respect Instagram's Terms of Service
- ✅ Use responsibly and ethically
- ❌ Not use for spam or harassment

---

**Built with ❤️ for Instagram story analytics**

*Not affiliated with Meta or Instagram* 