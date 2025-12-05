🎬 Letterboxd Wrapped (Quick Edition)Your movie year in review, instantly.A Streamlit-powered web application that generates a "Spotify Wrapped" style report for your recent Letterboxd activity. No API keys required—just enter your username!✨ Features⚡ Quick Wrap: Fetches your last 50 watched films via public RSS feeds instantly.🎢 Story Mode: Navigate through 10 interactive slides visualizing your data.🧬 Cine-MBTI: Discover your unique "Movie Personality Type" (e.g., Explorer-Modernist-Critic-Binger).🔥 The Roast: Get roasted by an AI algorithm based on your rating habits and obsessions.🎵 Soundtrack: A dynamic playlist generated from the "vibe" of your watched films.📊 Interactive Charts:Rating Distribution Rollercoaster.Day-of-Week Rhythm Radar.Era/Decade Analysis.🖼️ Wall of Fame: A visual grid of your recently watched posters.📱 Mobile Friendly: Fully responsive design that looks great on phones.🚀 Quick StartPrerequisitesPython 3.8 or higherpip (Python package manager)InstallationClone the repository:git clone [https://github.com/yourusername/letterboxd-wrapped.git](https://github.com/yourusername/letterboxd-wrapped.git)
cd letterboxd-wrapped
Create a virtual environment (optional but recommended):python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
Install dependencies:pip install -r requirements.txt
Run the app:streamlit run app.py
Open your browser to http://localhost:8501.🛠️ Tech StackFrontend: StreamlitData Processing: PandasVisualization: PlotlyScraping/Parsing: BeautifulSoup4 & Requests📂 Project Structureletterboxd-wrapped/
├── app.py              # Main application logic
├── requirements.txt    # Python dependencies
├── README.md           # Documentation
├── LICENSE             # MIT License
└── .gitignore          # Ignored files
🤝 ContributingContributions are welcome! Please feel free to submit a Pull Request.Fork the ProjectCreate your Feature Branch (git checkout -b feature/AmazingFeature)Commit your Changes (git commit -m 'Add some AmazingFeature')Push to the Branch (git push origin feature/AmazingFeature)Open a Pull Request⚠️ DisclaimerThis project is a fan-made creation and is not affiliated with, endorsed by, or sponsored by Letterboxd. Data is retrieved via public RSS feeds available on user profiles.📄 LicenseDistributed under the MIT License. See LICENSE for more information.
