"""
HTML exporter for Instagram conversations.
Generates animated, fancy HTML output with proper Arabic text rendering.
"""

import os
import logging
import emoji
from datetime import datetime
import html
import json
import instagram_data_processor.utils as utils

logger = logging.getLogger(__name__)

class HTMLExporter:
    """
    HTML exporter for Instagram conversations.
    Creates animated, fancy HTML output with proper Arabic text rendering.
    """

    def __init__(self, output_dir):
        """
        Initialize the HTML exporter.

        Args:
            output_dir (str): Output directory for HTML files
        """
        self.output_dir = output_dir
        logger.info(f"Initialized HTML exporter with output directory: {output_dir}")

    def export(self, messages, target_user, my_name, stats=None):
        """
        Export conversation to HTML file.

        Args:
            messages (list): List of processed messages
            target_user (str): Name of the target user
            my_name (str): Your name
            stats (dict, optional): Statistics dictionary

        Returns:
            str: Path to the exported HTML file
        """
        try:
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_with_{target_user}_{timestamp}.html"
            filepath = os.path.join(self.output_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as file:
                # Write HTML header
                file.write(self._generate_html_header(target_user, my_name))

                # Write statistics if available
                if stats:
                    file.write(self._generate_stats_section(stats, target_user, my_name))

                # Write conversation container opening
                file.write('<div class="conversation-container">\n')

                # Write messages
                current_date = None

                for msg in messages:
                    # Check if we need to add a date separator
                    date_str = msg['date']
                    if date_str != current_date:
                        current_date = date_str
                        file.write(f'<div class="date-separator">{date_str}</div>\n')

                    # Format message
                    # Fix any broken text in sender name
                    sender = utils.fix_broken_text(msg['sender'])
                    time_str = msg['time']
                    content = msg['content'] if msg['content'] else ""

                    # Determine message class based on sender
                    msg_class = "message-me" if sender == my_name else "message-other"

                    # Start message container
                    file.write(f'<div class="message-container {msg_class}-container">\n')

                    # Message bubble with animation
                    file.write(f'<div class="message-bubble {msg_class}" data-animation="fade-in">\n')

                    # Sender and time
                    file.write(f'<div class="message-header">\n')
                    file.write(f'<span class="sender">{html.escape(sender)}</span>\n')
                    file.write(f'<span class="time">{time_str}</span>\n')
                    file.write('</div>\n')

                    # Content - with special handling for Arabic text
                    if content:
                        # Fix any broken text encoding using the utils.fix_broken_text function
                        content = utils.fix_broken_text(content)

                        # Check if content contains Arabic characters
                        has_arabic = any(ord(c) >= 0x0600 and ord(c) <= 0x06FF for c in content)
                        content_class = "arabic-text" if has_arabic else ""

                        # Add the message content
                        file.write(f'<div class="message-content {content_class}">{html.escape(content)}</div>\n')

                        # Add emoji count if there are emojis
                        if msg['emoji_count'] > 0:
                            emoji_list = ', '.join(msg['emojis'])
                            file.write(f'<div class="emoji-count">Emojis: {msg["emoji_count"]} ({emoji_list})</div>\n')

                    # Media indicators
                    media_indicators = []
                    if msg['photos']:
                        media_indicators.append(f"📷 {len(msg['photos'])} photo(s)")
                    if msg['videos']:
                        media_indicators.append(f"🎬 {len(msg['videos'])} video(s)")
                    if msg['audio']:
                        media_indicators.append(f"🎵 {len(msg['audio'])} audio(s)")

                    if media_indicators:
                        media_str = " | ".join(media_indicators)
                        file.write(f'<div class="media-info">{media_str}</div>\n')

                    # Reactions
                    if msg['reactions']:
                        file.write('<div class="reactions">\n')
                        for reaction in msg['reactions']:
                            reaction_emoji = reaction['reaction']
                            actor = reaction['actor']
                            file.write(f'<span class="reaction" data-animation="bounce">{reaction_emoji} by {html.escape(actor)}</span>\n')
                        file.write('</div>\n')

                    # Close message bubble
                    file.write('</div>\n')

                    # Close message container
                    file.write('</div>\n')

                # Close conversation container
                file.write('</div>\n')

                # Write HTML footer with JavaScript for animations
                file.write(self._generate_html_footer())

            logger.info(f"Exported conversation to HTML file: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error exporting to HTML file: {str(e)}")
            return None

    def _generate_html_header(self, target_user, my_name):
        """
        Generate HTML header with CSS styles.

        Args:
            target_user (str): Name of the target user
            my_name (str): Your name

        Returns:
            str: HTML header
        """
        return f'''<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Instagram conversation with {html.escape(target_user)}">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>Conversation with {html.escape(target_user)}</title>
    <!-- Google Fonts for better Arabic support -->
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;700&display=swap">
    <style>
        /* General styles */
        @font-face {{
            font-family: 'Noto Sans Arabic';
            src: url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;700&display=swap');
            font-display: swap;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
        }}

        .container {{
            max-width: 800px;
            margin: 0 auto;
            background-color: #fff;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}

        /* Header styles */
        .header {{
            background: linear-gradient(135deg, #405de6, #5851db, #833ab4, #c13584, #e1306c, #fd1d1d);
            color: white;
            padding: 20px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}

        .header h1 {{
            margin: 0;
            font-size: 24px;
            position: relative;
            z-index: 2;
        }}

        .header p {{
            margin: 5px 0 0;
            opacity: 0.9;
            position: relative;
            z-index: 2;
        }}

        /* Animated background for header */
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, rgba(255,255,255,0.1) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0.1) 75%, transparent 75%, transparent);
            background-size: 30px 30px;
            z-index: 1;
            animation: move-background 15s linear infinite;
        }}

        @keyframes move-background {{
            0% {{ background-position: 0 0; }}
            100% {{ background-position: 60px 60px; }}
        }}

        /* Stats section */
        .stats-container {{
            padding: 20px;
            background-color: #f9f9f9;
            border-bottom: 1px solid #eee;
        }}

        .stats-container h2 {{
            margin-top: 0;
            color: #333;
            font-size: 18px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
        }}

        .stat-card {{
            background-color: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}

        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #e1306c;
            margin-bottom: 5px;
        }}

        .stat-label {{
            color: #666;
            font-size: 14px;
        }}

        /* Conversation styles */
        .conversation-container {{
            padding: 20px;
            display: flex;
            flex-direction: column;
        }}

        .date-separator {{
            text-align: center;
            margin: 20px 0;
            position: relative;
            color: #999;
            font-size: 14px;
        }}

        .date-separator::before,
        .date-separator::after {{
            content: '';
            position: absolute;
            top: 50%;
            width: 40%;
            height: 1px;
            background-color: #eee;
        }}

        .date-separator::before {{
            left: 0;
        }}

        .date-separator::after {{
            right: 0;
        }}

        .message-container {{
            display: flex;
            margin-bottom: 15px;
            max-width: 80%;
        }}

        .message-me-container {{
            align-self: flex-end;
        }}

        .message-other-container {{
            align-self: flex-start;
        }}

        .message-bubble {{
            border-radius: 18px;
            padding: 10px 15px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            position: relative;
            overflow: hidden;
            animation-duration: 0.5s;
            animation-fill-mode: both;
        }}

        .message-me {{
            background: linear-gradient(135deg, #00c6ff, #0072ff);
            color: white;
            border-bottom-right-radius: 5px;
        }}

        .message-other {{
            background: linear-gradient(135deg, #f2f2f2, #e6e6e6);
            color: #333;
            border-bottom-left-radius: 5px;
        }}

        .message-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
            font-size: 12px;
        }}

        .message-me .message-header {{
            color: rgba(255, 255, 255, 0.8);
        }}

        .message-other .message-header {{
            color: #999;
        }}

        .message-content {{
            word-wrap: break-word;
            margin-bottom: 5px;
        }}

        .emoji-count {{
            font-size: 12px;
            margin-top: 3px;
            padding: 2px 6px;
            background-color: rgba(0, 0, 0, 0.1);
            border-radius: 10px;
            display: inline-block;
            color: #666;
        }}

        .message-me .emoji-count {{
            background-color: rgba(255, 255, 255, 0.3);
            color: rgba(255, 255, 255, 0.9);
        }}

        /* Special handling for Arabic text */
        .arabic-text {{
            direction: rtl;
            text-align: right;
            font-family: 'Noto Sans Arabic', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif, 'Arial Unicode MS', sans-serif;
            unicode-bidi: bidi-override;
            line-height: 1.8;
            letter-spacing: 0.5px;
            font-weight: 400;
            font-size: 1.05em;
        }}

        .media-info {{
            font-size: 12px;
            margin-top: 5px;
            opacity: 0.8;
        }}

        .message-me .media-info {{
            color: rgba(255, 255, 255, 0.9);
        }}

        .reactions {{
            display: flex;
            flex-wrap: wrap;
            margin-top: 5px;
            gap: 5px;
        }}

        .reaction {{
            font-size: 12px;
            background-color: rgba(0, 0, 0, 0.1);
            padding: 2px 6px;
            border-radius: 10px;
            display: inline-block;
        }}

        .message-me .reaction {{
            background-color: rgba(255, 255, 255, 0.2);
        }}

        /* Animations */
        @keyframes fade-in {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        @keyframes bounce {{
            0%, 20%, 50%, 80%, 100% {{ transform: translateY(0); }}
            40% {{ transform: translateY(-10px); }}
            60% {{ transform: translateY(-5px); }}
        }}

        /* Responsive design */
        @media (max-width: 600px) {{
            .container {{
                border-radius: 0;
                box-shadow: none;
            }}

            .message-container {{
                max-width: 90%;
            }}

            .stats-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Conversation with {html.escape(target_user)}</h1>
            <p>Instagram Memory Book</p>
        </div>
'''

    def _generate_stats_section(self, stats, target_user, my_name):
        """
        Generate HTML for the statistics section.

        Args:
            stats (dict): Statistics dictionary
            target_user (str): Name of the target user
            my_name (str): Your name

        Returns:
            str: HTML for statistics section
        """
        html_content = '''
        <div class="stats-container">
            <h2>Conversation Statistics</h2>
            <div class="stats-grid">
'''

        # Total messages
        html_content += f'''
                <div class="stat-card" data-animation="fade-in">
                    <div class="stat-value">{stats['total_messages']}</div>
                    <div class="stat-label">Total Messages</div>
                </div>
'''

        # Messages by sender
        for sender, count in stats['messages_by_sender'].items():
            html_content += f'''
                <div class="stat-card" data-animation="fade-in">
                    <div class="stat-value">{count}</div>
                    <div class="stat-label">Messages from {html.escape(sender)}</div>
                </div>
'''

        # Total emojis
        html_content += f'''
                <div class="stat-card" data-animation="fade-in">
                    <div class="stat-value">{stats['total_emojis']}</div>
                    <div class="stat-label">Total Emojis</div>
                </div>
'''

        # Conversation duration
        html_content += f'''
                <div class="stat-card" data-animation="fade-in">
                    <div class="stat-value">{stats['conversation_duration_days']}</div>
                    <div class="stat-label">Conversation Days</div>
                </div>
'''

        # First and last message dates
        html_content += f'''
                <div class="stat-card" data-animation="fade-in">
                    <div class="stat-value">{stats['first_message_date']}</div>
                    <div class="stat-label">First Message</div>
                </div>

                <div class="stat-card" data-animation="fade-in">
                    <div class="stat-value">{stats['last_message_date']}</div>
                    <div class="stat-label">Last Message</div>
                </div>
'''

        # Most active day
        html_content += f'''
                <div class="stat-card" data-animation="fade-in">
                    <div class="stat-value">{stats['most_active_day']}</div>
                    <div class="stat-label">Most Active Day ({stats['most_active_day_count']} messages)</div>
                </div>
'''

        html_content += '''
            </div>
        </div>
'''
        return html_content

    def _generate_html_footer(self):
        """
        Generate HTML footer with JavaScript for animations.

        Returns:
            str: HTML footer
        """
        return '''
    </div>

    <script>
        // Animation functions
        document.addEventListener('DOMContentLoaded', function() {
            // Apply animations to elements with data-animation attribute
            const animatedElements = document.querySelectorAll('[data-animation]');

            // Create an Intersection Observer
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const animation = entry.target.getAttribute('data-animation');
                        entry.target.style.animationName = animation;
                        observer.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.1
            });

            // Observe each animated element
            animatedElements.forEach(element => {
                observer.observe(element);
            });

            // Apply staggered animation to message bubbles
            const messageBubbles = document.querySelectorAll('.message-bubble');
            messageBubbles.forEach((bubble, index) => {
                bubble.style.animationDelay = `${index * 0.1}s`;
            });

            // Apply bounce animation to reactions
            const reactions = document.querySelectorAll('.reaction');
            reactions.forEach((reaction, index) => {
                reaction.style.animationDelay = `${index * 0.2}s`;
                reaction.style.animationName = 'bounce';
                reaction.style.animationDuration = '1s';
                reaction.style.animationIterationCount = '1';
            });

            // Apply fade-in animation to stat cards
            const statCards = document.querySelectorAll('.stat-card');
            statCards.forEach((card, index) => {
                card.style.animationDelay = `${index * 0.1}s`;
                card.style.animationName = 'fade-in';
                card.style.animationDuration = '0.5s';
                card.style.animationFillMode = 'both';
            });
        });
    </script>
</body>
</html>
'''
