"""
Dashboard HTML Template Generation
"""

def get_dashboard_html(project_id: str, metadata: dict) -> str:
    """Generate the dashboard HTML"""
    
    stages_html = ""
    for stage_name, stage_info in metadata.get("stages", {}).items():
        status = stage_info.get("status", "pending")
        status_class = f"status-{status}"
        status_icon = get_status_icon(status)
        
        stages_html += f"""
        <div class="stage-card {status_class}">
            <div class="stage-header">
                <span class="status-icon">{status_icon}</span>
                <h3 class="stage-name">{format_stage_name(stage_name)}</h3>
                <span class="status-badge">{status.upper()}</span>
            </div>
            <div class="stage-details">
                <p class="started-at">{stage_info.get('started_at', 'Not started')}</p>
                <p class="completed-at">{stage_info.get('completed_at', 'In progress...')}</p>
            </div>
            <div class="stage-logs">
                <button class="view-logs-btn" onclick="viewLogs('{stage_name}')">View Logs</button>
            </div>
        </div>
        """
    
    input_files_html = ""
    for file in metadata.get("input_files", []):
        input_files_html += f"<li class='input-file'>{file}</li>"
    
    overall_status = metadata.get("status", "unknown")
    overall_status_class = f"status-{overall_status}"
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NGS Pipeline - Project {project_id}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        
        .project-meta {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .meta-item {{
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .meta-item .label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            font-weight: 600;
        }}
        
        .meta-item .value {{
            font-size: 16px;
            color: #333;
            margin-top: 5px;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .status-pending {{
            background: #e3f2fd;
            color: #1976d2;
        }}
        
        .status-running {{
            background: #fff3e0;
            color: #f57c00;
            animation: pulse 2s infinite;
        }}
        
        .status-completed {{
            background: #e8f5e9;
            color: #388e3c;
        }}
        
        .status-failed {{
            background: #ffebee;
            color: #d32f2f;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}
        
        .input-files {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .input-files h2 {{
            color: #333;
            margin-bottom: 15px;
            font-size: 18px;
        }}
        
        .input-files ul {{
            list-style: none;
        }}
        
        .input-file {{
            padding: 12px;
            background: #f8f9fa;
            margin-bottom: 10px;
            border-radius: 6px;
            border-left: 3px solid #667eea;
            color: #333;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 14px;
        }}
        
        .pipeline-stages {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        
        .pipeline-stages h2 {{
            color: #333;
            margin-bottom: 30px;
            font-size: 20px;
        }}
        
        .stages-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .stage-card {{
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            transition: all 0.3s ease;
        }}
        
        .stage-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .stage-card.status-completed {{
            border-color: #388e3c;
            background: #f1f8e9;
        }}
        
        .stage-card.status-running {{
            border-color: #f57c00;
            background: #fff8e1;
            border-left: 5px solid #f57c00;
        }}
        
        .stage-card.status-failed {{
            border-color: #d32f2f;
            background: #ffebee;
        }}
        
        .stage-card.status-pending {{
            border-color: #1976d2;
            background: #e3f2fd;
        }}
        
        .stage-header {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            gap: 10px;
        }}
        
        .status-icon {{
            font-size: 24px;
        }}
        
        .stage-name {{
            flex: 1;
            color: #333;
            font-size: 16px;
            margin: 0;
        }}
        
        .stage-details {{
            font-size: 13px;
            color: #666;
            margin-bottom: 15px;
            line-height: 1.6;
        }}
        
        .stage-details p {{
            margin: 5px 0;
        }}
        
        .view-logs-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        
        .view-logs-btn:hover {{
            background: #764ba2;
            transform: scale(1.05);
        }}
        
        .logs-modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            animation: fadeIn 0.3s ease;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        .modal-content {{
            background: white;
            margin: 5% auto;
            padding: 30px;
            border-radius: 10px;
            width: 90%;
            max-width: 900px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            max-height: 80vh;
            overflow-y: auto;
        }}
        
        .modal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}
        
        .modal-header h2 {{
            color: #333;
        }}
        
        .close-btn {{
            font-size: 28px;
            font-weight: bold;
            color: #aaa;
            cursor: pointer;
            background: none;
            border: none;
        }}
        
        .close-btn:hover {{
            color: #000;
        }}
        
        .log-content {{
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            border-radius: 6px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 13px;
            max-height: 500px;
            overflow-y: auto;
            line-height: 1.6;
        }}
        
        .log-line {{
            white-space: pre-wrap;
            word-break: break-word;
            margin: 2px 0;
        }}
        
        .artifacts {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        
        .artifacts h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 20px;
        }}
        
        .artifacts-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
        }}
        
        .artifact-item {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            transition: all 0.3s ease;
        }}
        
        .artifact-item:hover {{
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .artifact-name {{
            color: #333;
            font-weight: 600;
            margin-bottom: 10px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 13px;
            word-break: break-all;
        }}
        
        .artifact-info {{
            font-size: 12px;
            color: #666;
            margin-bottom: 10px;
        }}
        
        .download-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        
        .download-btn:hover {{
            background: #764ba2;
        }}
        
        .refresh-info {{
            text-align: center;
            color: #666;
            font-size: 13px;
            margin-top: 30px;
            padding-top: 30px;
            border-top: 1px solid #e0e0e0;
        }}
        
        .footer {{
            text-align: center;
            color: white;
            margin-top: 30px;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧬 NGS Pipeline Project Dashboard</h1>
            <p style="color: #666; margin-top: 5px;">Real-time monitoring and execution status</p>
            
            <div class="project-meta">
                <div class="meta-item">
                    <div class="label">Project ID</div>
                    <div class="value">{project_id}</div>
                </div>
                <div class="meta-item">
                    <div class="label">Status</div>
                    <div class="value">
                        <span class="status-badge {overall_status_class}">{overall_status.upper()}</span>
                    </div>
                </div>
                <div class="meta-item">
                    <div class="label">Created</div>
                    <div class="value">{format_datetime(metadata.get('created_at', 'Unknown'))}</div>
                </div>
                <div class="meta-item">
                    <div class="label">Started</div>
                    <div class="value">{format_datetime(metadata.get('started_at', 'Not started'))}</div>
                </div>
            </div>
        </div>
        
        <div class="input-files">
            <h2>📁 Input Files</h2>
            <ul>
                {input_files_html if input_files_html else '<li class="input-file" style="color: #999;">No input files</li>'}
            </ul>
        </div>
        
        <div class="pipeline-stages">
            <h2>🔄 Pipeline Execution Status</h2>
            <div class="stages-grid">
                {stages_html}
            </div>
        </div>
        
        <div class="artifacts">
            <h2>📦 Output Artifacts</h2>
            <div id="artifacts-list" class="artifacts-list">
                <p style="color: #999;">Loading artifacts...</p>
            </div>
        </div>
        
        <div class="refresh-info">
            <p>This dashboard refreshes automatically every 5 seconds</p>
            <p>Last updated: <span id="last-update">{datetime.now().isoformat()}</span></p>
        </div>
        
        <div class="footer">
            <p>NGS Pipeline Web Wrapper v1.0 | Built with FastAPI + HTML5</p>
        </div>
    </div>
    
    <!-- Logs Modal -->
    <div id="logs-modal" class="logs-modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="logs-title">Stage Logs</h2>
                <button class="close-btn" onclick="closeLogs()">&times;</button>
            </div>
            <div id="logs-content" class="log-content">
                <p style="color: #666;">Loading logs...</p>
            </div>
        </div>
    </div>
    
    <script>
        const PROJECT_ID = '{project_id}';
        const API_BASE = '/api';
        
        // Auto-refresh dashboard
        async function refreshDashboard() {{
            try {{
                // Update last updated time
                document.getElementById('last-update').textContent = new Date().toLocaleString();
                
                // Fetch artifacts
                const response = await fetch(`${{API_BASE}}/projects/${{PROJECT_ID}}/artifacts`);
                if (response.ok) {{
                    const data = await response.json();
                    updateArtifactsList(data.artifacts);
                }} else {{
                    console.error('Failed to fetch artifacts:', response.statusText);
                }}
            }} catch (error) {{
                console.error('Error refreshing dashboard:', error);
            }}
        }}
        
        function updateArtifactsList(artifacts) {{
            const container = document.getElementById('artifacts-list');
            
            if (artifacts.length === 0) {{
                container.innerHTML = '<p style="color: #999;">No artifacts yet</p>';
                return;
            }}
            
            container.innerHTML = artifacts.map(artifact => `
                <div class="artifact-item">
                    <div class="artifact-name">${{artifact.name}}</div>
                    <div class="artifact-info">
                        <div>Size: ${{formatBytes(artifact.size)}}</div>
                        <div>Modified: ${{new Date(artifact.modified).toLocaleString()}}</div>
                    </div>
                    <a href="${{artifact.path}}" class="download-btn" download>⬇️ Download</a>
                </div>
            `).join('');
        }}
        
        async function viewLogs(stage) {{
            try {{
                const response = await fetch(`${{API_BASE}}/projects/${{PROJECT_ID}}/logs/${{stage}}`);
                if (response.ok) {{
                    const data = await response.json();
                    showLogsModal(stage, data.logs);
                }} else {{
                    alert('Failed to fetch logs');
                }}
            }} catch (error) {{
                console.error('Error fetching logs:', error);
                alert('Error fetching logs: ' + error.message);
            }}
        }}
        
        function showLogsModal(stage, logs) {{
            const modal = document.getElementById('logs-modal');
            const title = document.getElementById('logs-title');
            const content = document.getElementById('logs-content');
            
            title.textContent = `${{stage.toUpperCase()}} - Logs`;
            
            if (logs.length === 0) {{
                content.innerHTML = '<p style="color: #666;">No logs available for this stage</p>';
            }} else {{
                content.innerHTML = logs.map(line => 
                    `<div class="log-line">${{escapeHtml(line)}}</div>`
                ).join('');
            }}
            
            modal.style.display = 'block';
        }}
        
        function closeLogs() {{
            document.getElementById('logs-modal').style.display = 'none';
        }}
        
        function formatBytes(bytes) {{
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
        }}
        
        function escapeHtml(text) {{
            const map = {{
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            }};
            return text.replace(/[&<>"']/g, m => map[m]);
        }}
        
        // Close modal when clicking outside
        window.onclick = function(event) {{
            const modal = document.getElementById('logs-modal');
            if (event.target === modal) {{
                modal.style.display = 'none';
            }}
        }}
        
        // Initial refresh and set up auto-refresh
        refreshDashboard();
        setInterval(refreshDashboard, 5000);
    </script>
</body>
</html>
"""
    
    return html


def get_status_icon(status: str) -> str:
    """Get emoji icon for status"""
    icons = {
        "pending": "⏳",
        "running": "⚙️",
        "completed": "✅",
        "failed": "❌",
        "paused": "⏸️"
    }
    return icons.get(status, "❓")


def format_stage_name(stage: str) -> str:
    """Format stage name for display"""
    name_map = {
        "getting_data": "Data Download & Conversion",
        "fastqc_raw": "Raw Quality Control",
        "trimming": "Read Trimming",
        "fastqc_trim": "Trimmed Quality Control",
        "multiqc_raw": "Raw QC Report",
        "multiqc_trim": "Trimmed QC Report",
        "reference": "Reference Indexing",
        "bwa_alignment": "Read Alignment",
        "samtools_sort": "BAM Sorting",
        "variant_calling": "Variant Calling",
        "consensus": "Consensus Generation",
        "cds_extraction": "CDS Extraction"
    }
    return name_map.get(stage, stage.replace("_", " ").title())


def format_datetime(dt_str: str) -> str:
    """Format datetime string"""
    if not dt_str or dt_str == "Not started":
        return "Not started"
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return dt_str
