# -*- coding: utf-8 -*-
"""
CSS styles for BDS KhangNgo offline viewer.
"""

BASE_CSS = """
        :root {
            --bg-color: #0f172a;
            --card-bg: rgba(30, 41, 59, 0.7);
            --border-color: rgba(255, 255, 255, 0.08);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --primary-color: #38bdf8;
            --accent-color: #f43f5e;
            --success-color: #10b981;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            line-height: 1.6;
            padding: 20px;
            background-image: radial-gradient(circle at 10% 20%, rgba(56, 189, 248, 0.05) 0%, transparent 40%),
                              radial-gradient(circle at 90% 80%, rgba(244, 63, 94, 0.03) 0%, transparent 40%);
            background-attachment: fixed;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            margin-bottom: 20px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
        }
        
        .header-title h1 {
            font-size: 28px;
            font-weight: 700;
            color: var(--primary-color);
            letter-spacing: -0.5px;
        }
        
        .header-title p {
            font-size: 14px;
            color: var(--text-muted);
        }
        
        .tag-status {
            background: rgba(56, 189, 248, 0.15);
            color: var(--primary-color);
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            border: 1px solid rgba(56, 189, 248, 0.3);
        }
        
        .grid-info {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        @media (max-width: 768px) {
            .grid-info {
                grid-template-columns: 1fr;
            }
            .header {
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }
        }
        
        .card {
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
        }
        
        .section-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 16px;
            color: var(--primary-color);
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 8px;
        }
        
        .info-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .info-table td {
            padding: 10px 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.03);
            vertical-align: top;
        }
        
        .info-table td.label {
            color: var(--text-muted);
            width: 40%;
            font-weight: 500;
        }
        
        .info-table td.value {
            color: var(--text-main);
            font-weight: 600;
        }
        
        .description-box {
            white-space: pre-wrap;
            color: #cbd5e1;
            font-size: 15px;
            margin-bottom: 16px;
            background: rgba(15, 23, 42, 0.4);
            padding: 16px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.03);
        }
        
        .usp-box {
            background: rgba(16, 185, 129, 0.08);
            border: 1px solid rgba(16, 185, 129, 0.2);
            color: #a7f3d0;
            padding: 16px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-weight: 500;
        }
        
        .grid-criteria {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 12px;
            margin-top: 10px;
            margin-bottom: 20px;
        }
        
        .criteria-card {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border-color);
            padding: 12px;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        
        .criteria-label {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-muted);
        }
        
        .criteria-value {
            font-size: 13px;
            font-weight: 600;
            color: var(--text-main);
        }
        
        .image-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
            margin-bottom: 30px;
        }
        
        .image-wrapper {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--border-color);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            aspect-ratio: 4/3;
            background: #000;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .image-wrapper img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
        }
        
        .image-wrapper:hover img {
            transform: scale(1.05);
        }
        
        .diagram-grid .image-wrapper {
            aspect-ratio: auto;
            max-height: 500px;
        }
        
        .diagram-grid .image-wrapper img {
            object-fit: contain;
            height: auto;
            max-height: 500px;
        }
        
        .btn-link {
            display: inline-block;
            background: var(--primary-color);
            color: #0f172a;
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.2s ease;
            margin-top: 10px;
            text-align: center;
            width: 100%;
        }
        
        .btn-link:hover {
            background: #7dd3fc;
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
        }
"""
