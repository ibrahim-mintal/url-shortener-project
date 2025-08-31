from flask import Flask, request, jsonify, redirect, render_template_string
import sqlite3
import hashlib
import time
import random
import string
import os

app = Flask(__name__)

# Database setup
DB_PATH = '/app/data/urls.db' if os.path.exists('/app') else './data/urls.db'

def init_db():
    """Initialize the SQLite database"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT UNIQUE NOT NULL,
            long_url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at: {DB_PATH}")

def generate_short_code(url, length=6):
    """Generate a short code for the URL"""
    # Use hash + random for better distribution
    hash_obj = hashlib.md5(url.encode())
    hash_hex = hash_obj.hexdigest()
    
    # Add some randomness to avoid collisions
    random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=3))
    
    # Combine and truncate
    combined = hash_hex + random_chars
    return combined[:length]

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Serve the web interface"""
    # Read the HTML file content (you'll save it as index.html)
    try:
        with open('index.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return '''
        <h1>URL Shortener API</h1>
        <p>Save the web interface as "index.html" in your project directory to use the browser interface.</p>
        <h2>API Usage:</h2>
        <pre>
# Shorten URL:
curl -X POST http://localhost:5000/shorten \\
  -H "Content-Type: application/json" \\
  -d '{"url": "https://www.example.com"}'

# Visit shortened URL:
curl -I http://localhost:5000/SHORT_CODE
        </pre>
        <p><a href="/health">Health Check</a> | <a href="/stats">Stats</a> | <a href="/list">List URLs</a></p>
        '''

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': time.time()})

@app.route('/shorten', methods=['POST'])
def shorten_url():
    """Shorten a URL"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        long_url = data['url']
        
        # Validate URL (basic check)
        if not long_url.startswith(('http://', 'https://')):
            return jsonify({'error': 'URL must start with http:// or https://'}), 400
        
        # Generate short code
        short_code = generate_short_code(long_url)
        
        # Check for collisions and regenerate if needed
        conn = get_db_connection()
        cursor = conn.cursor()
        
        max_attempts = 5
        for attempt in range(max_attempts):
            cursor.execute('SELECT id FROM urls WHERE short_code = ?', (short_code,))
            if cursor.fetchone() is None:
                break
            short_code = generate_short_code(long_url + str(attempt))
        else:
            conn.close()
            return jsonify({'error': 'Failed to generate unique short code'}), 500
        
        # Insert into database
        cursor.execute(
            'INSERT INTO urls (short_code, long_url) VALUES (?, ?)',
            (short_code, long_url)
        )
        conn.commit()
        conn.close()
        
        print(f"✅ Shortened URL: {long_url} -> {short_code}")
        
        response = {
            'short_code': short_code,
            'short_url': f'http://localhost:5000/{short_code}',
            'long_url': long_url
        }
        
        return jsonify(response), 201
    
    except Exception as e:
        print(f"❌ Error shortening URL: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/<short_code>')
def redirect_url(short_code):
    """Redirect to the original URL"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT long_url FROM urls WHERE short_code = ?', (short_code,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            print(f"✅ Redirecting {short_code} -> {result['long_url']}")
            return redirect(result['long_url'])
        else:
            print(f"❌ Short code not found: {short_code}")
            return jsonify({'error': 'Short URL not found'}), 404
    
    except Exception as e:
        print(f"❌ Error during redirect: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/stats')
def get_stats():
    """Get basic statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as total FROM urls')
        total_urls = cursor.fetchone()['total']
        conn.close()
        
        return jsonify({
            'total_shortened_urls': total_urls,
            'service': 'URL Shortener',
            'version': '1.0.0'
        })
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/list')
def list_urls():
    """List all shortened URLs (for debugging)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT short_code, long_url, created_at FROM urls ORDER BY created_at DESC LIMIT 10')
        results = cursor.fetchall()
        conn.close()
        
        urls = []
        for row in results:
            urls.append({
                'short_code': row['short_code'],
                'long_url': row['long_url'],
                'created_at': row['created_at'],
                'short_url': f'http://localhost:5000/{row["short_code"]}'
            })
        
        return jsonify({
            'recent_urls': urls,
            'total_count': len(urls)
        })
    except Exception as e:
        print(f"❌ Error listing URLs: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting URL Shortener Service...")
    print("=" * 40)
    init_db()
    print(f"🌐 Service will be available at: http://localhost:5000")
    print(f"📊 Health check: http://localhost:5000/health")
    print(f"📈 Stats: http://localhost:5000/stats")
    print("=" * 40)
    app.run(host='0.0.0.0', port=5000, debug=True)