#!/usr/bin/env python3
"""
Database Viewer - Simple web interface to browse startup data
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# Load startup data
STARTUPS_FILE = 'api/startups_data.json'
startups_data = []

def load_startups():
    global startups_data
    if os.path.exists(STARTUPS_FILE):
        with open(STARTUPS_FILE, 'r') as f:
            startups_data = json.load(f)
        print(f"Loaded {len(startups_data)} startups")
    else:
        print(f"Warning: {STARTUPS_FILE} not found")

load_startups()

@app.route('/')
def index():
    return render_template('db_viewer.html')

@app.route('/api/startups')
def get_startups():
    """Get all startups with optional filtering"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    search = request.args.get('search', '').lower()
    topic_filter = request.args.get('topic', '')
    tech_filter = request.args.get('tech', '')
    
    # Filter startups
    filtered = startups_data
    
    if search:
        filtered = [s for s in filtered if 
                   search in s.get('name', '').lower() or 
                   search in s.get('description', '').lower() or
                   search in s.get('shortDescription', '').lower()]
    
    if topic_filter:
        filtered = [s for s in filtered if topic_filter in s.get('topics', [])]
    
    if tech_filter:
        filtered = [s for s in filtered if tech_filter in s.get('tech', [])]
    
    # Pagination
    total = len(filtered)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = filtered[start:end]
    
    return jsonify({
        'startups': paginated,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    })

@app.route('/api/startup/<int:startup_id>')
def get_startup(startup_id):
    """Get a single startup by ID"""
    startup = next((s for s in startups_data if s['id'] == startup_id), None)
    if startup:
        return jsonify(startup)
    return jsonify({'error': 'Startup not found'}), 404

@app.route('/api/filters')
def get_filters():
    """Get all available filter options"""
    topics = set()
    techs = set()
    countries = set()
    
    for startup in startups_data:
        topics.update(startup.get('topics', []))
        techs.update(startup.get('tech', []))
        country = startup.get('billingCountry')
        if country:
            countries.add(country)
    
    return jsonify({
        'topics': sorted(list(topics)),
        'techs': sorted(list(techs)),
        'countries': sorted(list(countries))
    })

@app.route('/api/stats')
def get_stats():
    """Get database statistics"""
    total_startups = len(startups_data)
    
    # Count by topics
    topics_count = {}
    techs_count = {}
    countries_count = {}
    
    for startup in startups_data:
        for topic in startup.get('topics', []):
            topics_count[topic] = topics_count.get(topic, 0) + 1
        for tech in startup.get('tech', []):
            techs_count[tech] = techs_count.get(tech, 0) + 1
        country = startup.get('billingCountry')
        if country:
            countries_count[country] = countries_count.get(country, 0) + 1
    
    return jsonify({
        'total_startups': total_startups,
        'topics': topics_count,
        'techs': techs_count,
        'countries': countries_count
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Startup Database Viewer")
    print("=" * 60)
    print(f"Total startups loaded: {len(startups_data)}")
    print("\nAccess the viewer at: http://localhost:5050")
    print("=" * 60)
    app.run(debug=True, port=5050, host='0.0.0.0')
