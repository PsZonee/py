import os
import json
import zipfile
import shutil
import webbrowser
import http.server
import socketserver
from cgi import FieldStorage
from io import BytesIO

# --- UI FRONTEND ENGINE (HTML, CSS, JS) ---
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebIntoApp - Local Studio Engine</title>
    <style>
        :root {
            --primary: #00bcd4;
            --primary-dark: #0097a7;
            --nav-bg: #ffffff;
            --bg: #f5f7fb;
            --text: #4a5568;
            --text-dark: #1a202c;
            --border: #e2e8f0;
            --success: #2ecc71;
        }
        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 0;
        }
        /* Top Navigation Bar */
        nav {
            background: var(--nav-bg);
            border-bottom: 1px solid var(--border);
            padding: 10px 60px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .logo {
            font-weight: 800;
            font-size: 22px;
            color: #2c3e50;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .logo span { color: var(--primary); }
        .nav-links {
            display: flex;
            gap: 25px;
            font-size: 14px;
            font-weight: 600;
        }
        .nav-links a { text-decoration: none; color: #7f8c8d; }
        .nav-links a.active { color: var(--primary-dark); border-bottom: 2px solid var(--primary); padding-bottom: 5px; }

        /* Main Workspace Container */
        .workspace {
            max-width: 1300px;
            margin: 40px auto;
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 30px;
            padding: 0 20px;
        }
        .card {
            background: #ffffff;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.03);
            border: 1px solid var(--border);
            padding: 30px;
        }
        .card-header h2 { margin: 0 0 5px 0; font-size: 22px; color: var(--text-dark); }
        .card-header p { margin: 0 0 25px 0; font-size: 14px; color: #94a3b8; }

        /* Tabs System */
        .tabs { display: flex; gap: 10px; margin-bottom: 25px; border-bottom: 1px solid var(--border); padding-bottom: 10px; }
        .tab-btn {
            background: #edf2f7; border: none; padding: 10px 20px; border-radius: 6px;
            font-weight: 600; cursor: pointer; color: var(--text); display: flex; align-items: center; gap: 8px;
        }
        .tab-btn.active { background: var(--primary); color: white; }

        /* Form Controls */
        .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
        .form-group { display: flex; flex-direction: column; gap: 8px; margin-bottom: 20px; }
        .form-group.full { grid-column: span 2; }
        label { font-size: 14px; font-weight: 600; color: var(--text-dark); }
        input[type="text"], input[type="number"], select {
            padding: 12px; border: 1px solid var(--border); border-radius: 6px; font-size: 14px;
            background: #f8fafc; transition: border 0.2s;
        }
        input:focus, select:focus { border-color: var(--primary); outline: none; background: #fff; }
        
        /* Interactive Upload Target */
        .file-dropzone {
            border: 2px dashed var(--primary); background: #f0fafd; padding: 20px;
            border-radius: 6px; text-align: center; cursor: pointer; position: relative;
        }
        .file-dropzone input[type="file"] {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; opacity: 0; cursor: pointer;
        }

        /* Action Buttons */
        .btn-submit {
            background: #2c3e50; color: white; border: none; padding: 14px 35px;
            font-size: 16px; font-weight: 700; border-radius: 6px; cursor: pointer;
            display: flex; align-items: center; gap: 10px; width: fit-content; margin-top: 10px;
        }
        .btn-submit:hover { background: #1a252f; }

        /* Right Panel / Extras Section */
        .extras-head { border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-bottom: 20px; }
        .extras-head h3 { margin: 0; font-size: 18px; color: var(--text-dark); }
        .extras-head p { margin: 2px 0 0 0; font-size: 12px; color: #94a3b8; }
        
        .icon-uploader-box {
            text-align: center; padding: 20px; border: 1px dashed var(--border);
            border-radius: 8px; margin-bottom: 20px; background: #fafafa;
        }
        .icon-preview {
            width: 90px; height: 90px; border-radius: 16px; margin: 0 auto 10px auto;
            background: #e2e8f0; display: flex; align-items: center; justify-content: center;
            overflow: hidden; border: 1px solid var(--border);
        }
        .icon-preview img { width: 100%; height: 100%; object-fit: cover; }

        .toggle-row {
            display: flex; justify-content: space-between; align-items: center;
            padding: 12px 0; border-bottom: 1px solid #f1f5f9; font-size: 14px; font-weight: 500;
        }
        .toggle-status {
            display: flex; align-items: center; gap: 5px; color: var(--success); font-weight: 700;
        }
    </style>
</head>
<body>

    <nav>
        <div class="logo">&lt; <span>WEBINTOAPP</span> &gt;</div>
        <div class="nav-links">
            <a href="#">Dashboard</a>
            <a href="#" class="active">App Maker</a>
            <a href="#">Apps</a>
            <a href="#">Installs</a>
            <a href="#">Settings</a>
            <a href="#">Support</a>
        </div>
    </nav>

    <div class="workspace">
        <div class="card">
            <div class="card-header">
                <h2>App Maker</h2>
                <p>Set the details of your App then click on the Next button.</p>
            </div>

            <form action="/generate" method="POST" enctype="multipart/form-data">
                <div class="tabs">
                    <button type="button" class="tab-btn active">📁 HTML Files / ZIP Asset</button>
                </div>

                <div class="form-group full">
                    <label>Upload App Source (index.html or complete game .zip pack)</label>
                    <div class="file-dropzone">
                        <strong id="file-label">Click to select files or drop here</strong>
                        <input type="file" name="web_file" accept=".html,.zip" onchange="document.getElementById('file-label').innerText = this.files[0].name" required>
                    </div>
                </div>

                <div class="form-grid">
                    <div class="form-group">
                        <label>Give your App a name</label>
                        <input type="text" name="app_name" value="MomuBloom" required>
                    </div>
                    <div class="form-group">
                        <label>Company / Brand Name</label>
                        <input type="text" name="company_name" value="Masarp Studio" required>
                    </div>
                </div>

                <div class="form-grid">
                    <div class="form-group">
                        <label>Major Version</label>
                        <input type="number" name="version_major" value="3" min="1" required>
                    </div>
                    <div class="form-group">
                        <label>Minor Version</label>
                        <input type="number" name="version_minor" value="0" min="0" required>
                    </div>
                </div>

                <div class="form-grid">
                    <div class="form-group">
                        <label>Package Name (Play Store ID)</label>
                        <input type="text" name="package_name" value="com.masarpstudio.momubloom" required>
                    </div>
                    <div class="form-group">
                        <label>Default Screen Orientation Mode</label>
                        <select name="orientation">
                            <option value="portrait">Portrait Only</option>
                            <option value="landscape">Landscape Only</option>
                            <option value="sensor">Sensor (Auto-Rotate)</option>
                        </select>
                    </div>
                </div>

                <button type="submit" class="btn-submit">Next &raquo;</button>
        </div>

        <div class="card" style="height: fit-content;">
            <div class="extras-head">
                <h3>Extras</h3>
                <p>Premium features (Optional)</p>
            </div>

            <div class="icon-uploader-box">
                <div class="icon-preview" id="icon-view">
                    <svg viewBox="0 0 100 100" width="60" height="60" style="fill: #e066ff;"><path d="M50 15c-12 0-20 10-20 22 0 15 15 28 20 33 5-5 20-18 20-33 0-12-8-22-20-22zm0 12c4 0 7 3 7 7s-3 7-7 7-7-3-7-7 3-7 7-7z"/></svg>
                </div>
                <label style="color:var(--primary); cursor:pointer; font-size:13px;">
                    Set Application Icon
                    <input type="file" name="app_icon" accept="image/png" style="display:none;" onchange="readIcon(this)">
                </label>
            </div>

            <div class="toggle-row">
                <span>App Toolbar</span>
                <span class="toggle-status">✓ Enabled</span>
            </div>
            <div class="toggle-row">
                <span>Splash Screen</span>
                <span style="color:#a0aec0; font-weight:bold;">ABC</span>
            </div>
            <div class="toggle-row">
                <span>Certification (Signing)</span>
                <span class="toggle-status">✓ Auto-Ready</span>
            </div>
            <div class="toggle-row">
                <span>Firebase Integration</span>
                <span style="color:#718096;">Inactive</span>
            </div>
            <div class="toggle-row">
                <span>AdMob Monetization</span>
                <span style="color:#718096;">Inactive</span>
            </div>
        </div>
        </form>
    </div>

    <script>
        function readIcon(input) {
            if (input.files && input.files[0]) {
                var reader = new FileReader();
                reader.onload = function(e) {
                    document.getElementById('icon-view').innerHTML = '<img src="' + e.target.result + '">';
                }
                reader.readAsDataURL(input.files[0]);
            }
        }
    </script>
</body>
</html>
"""

# --- ARCHITECTURE LAYER TEMPLATES (ANDROID NATIVE WRAPPER) ---

TEMPLATE_MANIFEST = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{package_name}">
    
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <application
        android:allowBackup="true"
        android:label="{app_name}"
        android:icon="@mipmap/ic_launcher"
        android:hardwareAccelerated="true"
        android:supportsRtl="true"
        android:theme="@android:style/Theme.NoTitleBar.Fullscreen">
        
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:screenOrientation="{orientation}"
            android:configChanges="orientation|screenSize|keyboardHidden|screenLayout">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
"""

TEMPLATE_ACTIVITY = """package {package_name};

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends Activity {{
    private WebView mWebView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        
        // Native Edge-to-Edge Immersive Display Flag Mapping
        getWindow().getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
            | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
            | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
            | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
            | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
            | View.SYSTEM_UI_FLAG_FULLSCREEN
        );

        mWebView = new WebView(this);
        setContentView(mWebView);

        WebSettings settings = mWebView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        
        // Keep rendering locked inside our WebView canvas wrapper
        mWebView.setWebViewClient(new WebViewClient());
        
        mWebView.loadUrl("file:///android_asset/index.html");
    }}

    @Override
    public void onBackPressed() {{
        if (mWebView.canGoBack()) {{
            mWebView.goBack();
        }} else {{
            super.onBackPressed();
        }}
    }}
}}
"""

TEMPLATE_APP_GRADLE = """plugins {{
    id 'com.android.application'
}}

android {{
    compileSdk 34
    namespace "{package_name}"

    defaultConfig {{
        applicationId "{package_name}"
        minSdk 24
        targetSdk 34
        versionCode {version_code}
        versionName "{version_name}"
    }}

    buildTypes {{
        release {{
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }}
    }}
}}
"""

TEMPLATE_ROOT_GRADLE = """buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:8.2.2'
    }
}
allprojects {
    repositories {
        google()
        mavenCentral()
    }
}
task clean(type: Delete) {
    delete rootProject.buildDir
}
"""

TEMPLATE_SETTINGS = """rootProject.name = "{app_name}"
include ':app'
"""

# --- COMPLIANCE CORE ENGINE SERVER ---

class StudioEngineHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(HTML_INTERFACE.encode('utf-8'))
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/generate":
            form = FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type']}
            )
            
            # Form extraction
            app_name = form.getvalue('app_name', 'UnnamedApp')
            company_name = form.getvalue('company_name', 'Studio')
            package_name = form.getvalue('package_name', 'com.studio.app')
            version_major = form.getvalue('version_major', '1')
            version_minor = form.getvalue('version_minor', '0')
            orientation = form.getvalue('orientation', 'portrait')
            
            output_dir = os.path.join(os.getcwd(), app_name.replace(" ", "_") + "_AndroidStudioProject")
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)
            
            # Directory Setup
            assets_dir = os.path.join(output_dir, "app", "src", "main", "assets")
            java_dir = os.path.join(output_dir, "app", "src", "main", "java", *package_name.split('.'))
            manifest_dir = os.path.join(output_dir, "app", "src", "main")
            mipmap_dir = os.path.join(output_dir, "app", "src", "main", "res", "mipmap")
            
            os.makedirs(assets_dir, exist_ok=True)
            os.makedirs(java_dir, exist_ok=True)
            os.makedirs(mipmap_dir, exist_ok=True)

            # Process Application Payload Asset files
            uploaded_file = form['web_file']
            filename = uploaded_file.filename
            file_data = uploaded_file.file.read()

            if filename.endswith('.zip'):
                with zipfile.ZipFile(BytesIO(file_data)) as zip_ref:
                    zip_ref.extractall(assets_dir)
            else:
                with open(os.path.join(assets_dir, "index.html"), "wb") as f:
                    f.write(file_data)

            # Handle Icon Upload fallback to plain square blueprint if empty
            if 'app_icon' in form and form['app_icon'].filename:
                icon_data = form['app_icon'].file.read()
                with open(os.path.join(mipmap_dir, "ic_launcher.png"), "wb") as f:
                    f.write(icon_data)
            else:
                # Fallback blank asset initialization layout
                with open(os.path.join(mipmap_dir, "ic_launcher.png"), "wb") as f:
                    f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x01\x00\x00\x0c\x00\x01\x04\x16\xe3\xa1\x00\x00\x00\x00IEND\xaeB`\x82')

            # Build configurations mappings
            with open(os.path.join(manifest_dir, "AndroidManifest.xml"), "w", encoding='utf-8') as f:
                f.write(TEMPLATE_MANIFEST.format(package_name=package_name, app_name=app_name, orientation=orientation))
                
            with open(os.path.join(java_dir, "MainActivity.java"), "w", encoding='utf-8') as f:
                f.write(TEMPLATE_ACTIVITY.format(package_name=package_name))

            with open(os.path.join(output_dir, "app", "build.gradle"), "w", encoding='utf-8') as f:
                f.write(TEMPLATE_APP_GRADLE.format(
                    package_name=package_name, 
                    version_code=version_major, 
                    version_name=f"{version_major}.{version_minor}"
                ))

            with open(os.path.join(output_dir, "build.gradle"), "w", encoding='utf-8') as f:
                f.write(TEMPLATE_ROOT_GRADLE)

            with open(os.path.join(output_dir, "settings.gradle"), "w", encoding='utf-8') as f:
                f.write(TEMPLATE_SETTINGS.format(app_name=app_name))

            # Success Feedback Screen
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            success_html = f"""
            <html>
            <body style="font-family: system-ui, sans-serif; text-align:center; padding:60px; background:#f5f7fb;">
                <div style="background:white; display:inline-block; padding:40px; border-radius:12px; box-shadow:0 10px 30px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; max-width: 600px;">
                    <div style="font-size: 50px; margin-bottom: 10px;">🚀</div>
                    <h1 style="color:#1a202c; margin-bottom:5px;">Project Wrapper Compiled!</h1>
                    <p style="color:#718096; margin-top:0;">Your production-grade workspace has been exported successfully.</p>
                    <div style="background:#f8fafc; border:1px solid #e2e8f0; padding:15px; border-radius:6px; font-family:monospace; font-size:13px; word-break:break-all; margin:25px 0; color:#2d3748; text-align:left;">
                        <strong>Path:</strong> {output_dir}
                    </div>
                    <p style="font-size:14px; color:#4a5568; text-align:left; line-height:1.6;">
                        <strong>Next Steps for Play Store Release:</strong><br>
                        1. Open <strong>Android Studio</strong> and select "Open existing project".<br>
                        2. Target this generated directory.<br>
                        3. Go to <strong>Build &gt; Generate Signed Bundle / APK</strong> to generate your release asset ready for delivery.
                    </p>
                    <a href="/" style="text-decoration:none; color:white; background:#00bcd4; padding:12px 25px; border-radius:6px; display:inline-block; font-weight:bold; margin-top:20px;">Build Another Package</a>
                </div>
            </body>
            </html>
            """
            self.wfile.write(success_html.encode('utf-8'))

def run():
    PORT = 8080
    with socketserver.TCPServer(("", PORT), StudioEngineHandler) as httpd:
        print(f"[Engine] Core server deployed at http://localhost:{PORT}")
        webbrowser.open(f"http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run()