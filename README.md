# 📚 SZABIST Timetable Scraper

<div align="center">

[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

*A smart solution for SZABIST students to automatically extract and organize daily timetable emails into a clean, filterable schedule view.*

[🚀 Features](#-features) • [📋 For Other Universities](#-for-other-universities) • [⚡ Quick Start](#-quick-start) • [🔧 Setup Guide](#-setup-guide) • [🤝 Contributing](#-contributing)

</div>

---

## 🌟 The Problem

**SZABIST sends timetable emails DAILY** 📧, which creates a major headache for students:

- 📬 **Daily Email Overload**: Every single day, you get a new timetable email
- 🔍 **Manual Searching**: Have to dig through your inbox daily to find your classes
- 📅 **Semester Filtering**: Need to manually filter out irrelevant semesters from the massive list
- ⏰ **Time Waste**: Spending precious minutes every day just to see "What classes do I have today?"
- 📱 **Mobile Unfriendly**: University emails are poorly formatted and hard to read on phones

## 💡 The Solution

This scraper **automatically**:
1. 🔐 **Connects to your Gmail** using secure OAuth (no password needed!)
2. 📨 **Finds SZABIST timetable emails** from your inbox
3. 🧠 **Extracts YOUR semester's classes** using smart filtering
4. 📊 **Displays them in a clean table** - sorted by time, day, and course
5. 👥 **Supports multiple users** - your roommates can use it too!

### ✨ What You Get
- **One-click access** to your daily schedule
- **Clean, mobile-friendly** table view
- **Semester filtering** - only see classes for semesters you care about
- **No more email hunting** - everything organized in one place
- **Shareable** - run it locally and let your friends use it too

---

## 🚀 Features

### � **Smart Email Processing**
- **SZABIST Email Recognition**: Automatically identifies timetable emails from SZABIST
- **Daily Auto-Sync**: Set it up once, get updates automatically
- **HTML Parsing**: Extracts clean data from messy university email formats
- **Duplicate Prevention**: Won't show the same class twice

### 🎯 **Semester Filtering**
- **Choose Your Semesters**: Only see classes for semesters you're enrolled in
- **Easy Management**: Add/remove semesters with simple clicks
- **Smart Organization**: Groups classes by semester, day, and time

### 📱 **Clean Interface**
- **Mobile-Friendly**: Works great on your phone during campus walks
- **Sortable Tables**: Click column headers to sort by time, course, room, etc.
- **Real-Time Status**: See when data was last updated
- **Multi-User**: Your friends can create their own profiles

### � **Secure & Private**
- **OAuth Login**: Uses Google's secure login (no passwords stored)
- **Personal Data**: Each user only sees their own timetable
- **Local Hosting**: Run it on your laptop/PC for full control

---

## 📋 For Other Universities

**This scraper is built for SZABIST** but can be adapted for other universities that send timetable emails! 

### � **To Use With Your University**:

1. **Check Email Format**: Your university must send timetable emails to Gmail
2. **Modify Email Parsing**: Update the parser in `backend/scraper/parser.py` to understand your university's email format
3. **Adjust Semester Logic**: Modify semester detection in `backend/scraper/semester_matcher.py`
4. **Test & Customize**: Run test scrapes and adjust the parsing logic as needed

### �️ **What Needs Changing**:
- **Email Subject Patterns**: How your university titles timetable emails
- **HTML Structure**: How the timetable data is formatted in emails
- **Semester Names**: Your university's semester naming convention
- **Course Code Format**: How your university formats course codes

*Want help adapting this for your university? Open an issue with sample emails (remove personal info) and I'll help!*

---

## 🔧 Setup Guide

### **📋 What You Need**
- **Computer with Python & Node.js** (Windows/Mac/Linux)
- **Gmail account** (your SZABIST email should forward here)
- **Google account** for API access (can be same as Gmail)
- **Supabase account** (free tier works fine)

### **⏱️ Time Required**: ~15-20 minutes for first-time setup

### **🎯 End Result**: 
A local web app running on your computer that automatically shows your SZABIST timetable in a clean format!

---

## ⚡ Quick Start

### **🚀 Step 1: Download the Code**
```bash
git clone https://github.com/muneeb-anjum0/Timetable-Wizard.git
cd Timetable-Wizard
```

### **🐍 Step 2: Setup Python Backend**

#### **Install Python Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

#### **Get Google Gmail API Access**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project (name it "SZABIST Scraper" or whatever you like)
3. Enable "Gmail API" 
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Choose "Desktop Application"
6. Download the JSON file and save it as `backend/credentials/client_secret.json`

#### **Setup Database (Supabase)**
1. Go to [Supabase](https://supabase.com) and create free account
2. Create new project
3. Go to Settings → API and copy:
   - Project URL
   - Service Role Key (the `service_role` one, not `anon`)

#### **Create Environment File**
Create `backend/.env` file:
```env
# Your Supabase details
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key_here

# Keep these as-is
TZ=Asia/Karachi
PORT=5000
```

#### **Setup Database Tables**
The app will create tables automatically, but you can create them manually in Supabase if needed.

### **⚛️ Step 3: Setup React Frontend**
```bash
cd ../frontend
npm install
```

### **🎉 Step 4: Start Everything**
From the main project folder:
```bash
# This starts both backend and frontend automatically
run.bat
```

**OR start manually:**
```bash
# Terminal 1 - Backend
cd backend
python app.py

# Terminal 2 - Frontend  
cd frontend
npm start
```

### **🌐 Step 5: Use the App**
1. Open browser to `http://localhost:3000`
2. Click "Sign in with Gmail" 
3. Allow access to your Gmail
4. Click "Refresh Data" to scrape your first timetable
5. Go to "Manage Semesters" and add your current semesters (e.g., "Fall 2025", "7th Semester")
6. Enjoy your clean, organized timetable! 🎊

---

## 📖 How to Use Daily

### **🌅 Daily Routine**
1. **Open the app**: `http://localhost:3000` 
2. **Check your schedule**: Your classes are already organized and ready!
3. **Need updates?**: Click "Refresh Data" if you got new timetable emails

### **⚙️ First-Time Setup Tasks**
- **Add your semesters**: Click "Manage Semesters" and add things like "Fall 2025", "8th Semester", etc.
- **Test the scraper**: Click "Refresh Data" to make sure it finds your SZABIST emails
- **Bookmark it**: Add `http://localhost:3000` to your browser bookmarks

### **👥 Sharing with Friends**
Your friends can use the same app:
1. **They need their own Gmail**: Each person signs in with their own Google account
2. **Same computer**: Multiple people can use the same running instance
3. **Their data is separate**: Everyone only sees their own timetable

### **🔄 Automated Updates** (Optional)
- The app can check for new emails automatically in the background
- You can set this up in the scheduler settings
- No need to manually refresh every day!

---

## 🐛 Troubleshooting

### **❌ Common Issues & Solutions**

#### **"Can't find timetable emails"**
- ✅ Make sure SZABIST emails are in your Gmail (check forwarding settings)
- ✅ Check if emails have subject containing "timetable" or "schedule"
- ✅ Try refreshing the data again

#### **"Google OAuth Error"**
- ✅ Make sure `client_secret.json` is in the right place
- ✅ Check your Google Cloud Console project is set up correctly
- ✅ Make sure Gmail API is enabled

#### **"Database Connection Error"**  
- ✅ Double-check your Supabase URL and Service Key in `.env`
- ✅ Make sure your Supabase project is running (not paused)

#### **"No classes showing up"**
- ✅ Add your semester names in "Manage Semesters" 
- ✅ Make sure the semester names match what's in your SZABIST emails
- ✅ Try different variations like "Fall 2025", "7th Semester", "BS-CS-7"

### **📞 Need Help?**
- Open an issue on GitHub with:
  - What error you're seeing
  - Which step you're stuck on  
  - Screenshot if possible (hide personal info!)

---

## 🤝 Contributing

### **🎯 Want to Help Make This Better?**

#### **🐛 Report Bugs**
- Found something broken? Open a GitHub issue!
- Include screenshots and error messages

#### **💡 Suggest Features**  
- Want a specific feature? Let me know in the issues!
- Ideas: calendar export, mobile app, better semester detection

#### **💻 Code Contributions**
1. Fork the repo
2. Make your changes
3. Test with your own SZABIST emails
4. Submit a pull request

#### **🏫 University Adaptations**
- Using this for another university? Share your modifications!
- Help others adapt it for their schools

---

## 📝 License

This project is open source under the MIT License. Feel free to use, modify, and share!

---

<div align="center">

**Built by a SZABIST student, for SZABIST students 🎓**

*Tired of checking emails every day? Let the robot do it! 🤖*

**Found this helpful? ⭐ Star the repo and share with your classmates!**

---

### 💬 Questions? Issues? Ideas?
[Open a GitHub Issue](https://github.com/muneeb-anjum0/Timetable-Wizard.git) • Made with ❤️ for the SZABIST community

</div>
