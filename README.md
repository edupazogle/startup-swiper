# 🚀 Startup Swiper

A modern startup discovery and meeting management platform for investors and venture capitalists.

## ✨ Features

- 🎯 **Smart Startup Discovery** - Tinder-like interface for browsing 4,374+ startups
- 📅 **Meeting Scheduling** - Built-in calendar and meeting management
- 🔔 **Push Notifications** - Web push notifications for upcoming meetings
- 🤖 **AI Concierge** - LLM-powered assistant for startup insights
- 📊 **Feedback System** - Structured post-meeting feedback and insights
- 🎨 **Modern UI** - Beautiful React interface with Radix UI components

## 🎬 Quick Start (Local Development)

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/startup-swiper.git
cd startup-swiper

# Run the launch script
./launch.sh
```

Visit:
- Frontend: http://localhost:5173
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🌐 Deploy to Production

### Option 1: Render.com (Recommended - 5 minutes)

1. **Push to GitHub**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/startup-swiper.git
   git push -u origin main
   ```

2. **Deploy on Render**
   - Go to [render.com](https://render.com)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Click "Apply"

3. **Set Environment Variables**
   
   In Render Dashboard for the API service:
   ```
   DATABASE_URL=sqlite:///./startup_swiper.db
   VAPID_PUBLIC_KEY=BIJjEmB_TRF29nRJ8uaOR_n3N5PnpxRd8I1r_2WHcSt0mMTCFnhwGAP6A2aWBKhUkwt82pDaNMAoRnodbQP1k3M
   VAPID_PRIVATE_KEY=jsvWNpTlUb7j_DfNAJL1qSkjT65pOO-YrUNTYure8Tw
   SECRET_KEY=your_secret_key_here
   ```
   
   For the Frontend service:
   ```
   VITE_API_URL=https://YOUR-API-NAME.onrender.com
   ```

4. **Done!** Share your URLs with testers 🎉

Full deployment guide: [DEPLOYMENT.md](./DEPLOYMENT.md)

## 👥 Pre-configured Test Users

All users have password: `123`

- nicolas.desaintromain@axa.com
- alice.jin@axa-uk.co.uk
- josep-oriol.ayats@axa.com
- wolfgang.sachsenhofer@axa.ch
- clarisse.montmaneix@axaxl.com
- adwaith.nair@axa.com

## 📁 Project Structure

```
startup-swiper/
├── api/                    # FastAPI backend
│   ├── main.py            # API entry point
│   ├── models.py          # Database models
│   ├── auth.py            # Authentication
│   ├── ai_concierge.py    # LLM integration
│   └── requirements.txt   # Python dependencies
├── app/startup-swipe-schedu/  # React frontend
│   ├── src/               # React components
│   ├── public/            # Static assets
│   └── package.json       # Node dependencies
├── render.yaml            # Deployment configuration
└── launch.sh              # Local development script
```

## 🛠️ Technology Stack

**Frontend:**
- React 19 with TypeScript
- Vite for build tooling
- Radix UI components
- TailwindCSS
- React Query for state management

**Backend:**
- FastAPI (Python)
- SQLAlchemy ORM
- LiteLLM for AI integration
- JWT authentication
- Web Push notifications

## 📚 Documentation

- [Quick Start Guide](./QUICK_START.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [API Documentation](./api/README.md)
- [Notification System](./NOTIFICATION_SYSTEM_DOCS.md)
- [AI Concierge](./AI_CONCIERGE_SUMMARY.md)
- [Feedback System](./api/LLM_FEEDBACK_SYSTEM.md)

## 🔧 Development

### Backend Setup

```bash
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd app/startup-swipe-schedu
npm install
npm run dev
```

### Create Production Users

```bash
cd api
source venv/bin/activate
python3 create_prod_users.py
```

## 🧪 Testing

```bash
# Backend tests
cd api
pytest

# Frontend tests
cd app/startup-swipe-schedu
npm test
```

## 📝 Environment Variables

### Backend (.env)
```env
DATABASE_URL=sqlite:///./startup_swiper.db
SECRET_KEY=your_secret_key_here
VAPID_PUBLIC_KEY=your_vapid_public_key
VAPID_PRIVATE_KEY=your_vapid_private_key
OPENAI_API_KEY=your_openai_key  # Optional
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

## 🚀 Features in Detail

### Smart Startup Discovery
- Browse 4,374+ startups from Slush 2024
- Swipe interface with filtering
- Detailed startup profiles
- Save favorites and pass on others

### Meeting Management
- Schedule meetings with startups
- Calendar integration
- Automated reminders
- Meeting history tracking

### Push Notifications
- Real-time meeting reminders
- PWA support for mobile
- Custom notification timing
- Offline capability

### AI Concierge
- Ask questions about startups
- Get investment insights
- Compare startups
- Research assistance

### Feedback System
- AI-generated post-meeting questions
- Structured insight capture
- Learning from interactions
- Export capabilities

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues or questions:
1. Check the [documentation](./docs/)
2. Review [common issues](./DEPLOYMENT.md#common-issues)
3. Open an issue on GitHub

## 🎉 Acknowledgments

Built with ❤️ for the startup investment community.

---

**Ready to discover your next investment?** 🚀

Deploy now: [DEPLOYMENT.md](./DEPLOYMENT.md)
# Deployment Test - 2025-11-16 22:20:52 UTC
