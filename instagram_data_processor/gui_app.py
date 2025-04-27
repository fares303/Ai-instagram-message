"""
GUI Application for Instagram Data Processor.

This module provides a modern, animated GUI for the Instagram Data Processor
using CustomTkinter.
"""

import os
import json
import threading
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk

# Import the necessary modules from our package
from instagram_data_processor.json_processor import InstagramDataProcessor
from instagram_data_processor.media_extractor import MediaExtractor
from instagram_data_processor.exporters import TxtExporter, HTMLExporter, PDFExporter, ExcelExporter
import instagram_data_processor.utils as utils

# Set appearance mode and default color theme
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class InstagramDataProcessorApp(ctk.CTk):
    """
    Main application class for the Instagram Data Processor GUI.
    """

    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Instagram Memory Book Generator")
        self.geometry("900x600")
        self.minsize(800, 500)

        # Initialize variables
        self.folder_path = tk.StringVar()
        self.target_user = tk.StringVar()
        self.my_name = tk.StringVar()
        self.custom_words = tk.StringVar()
        self.output_path = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Instagram_Memory_Book"))
        self.is_group_chat = tk.BooleanVar(value=False)

        # Initialize state variables
        self.json_files = []
        self.valid_json_files = []
        self.is_analyzing = False
        self.analysis_complete = False
        self.analysis_results = None

        # Create UI elements
        self._create_ui()

    def _create_ui(self):
        """Create the user interface."""
        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Create header
        self._create_header()

        # Create folder selection section
        self._create_folder_selection()

        # Create user input section
        self._create_user_input()

        # Create custom words input section
        self._create_custom_words_input()

        # Create analyze button
        self._create_analyze_button()

        # Create progress section
        self._create_progress_section()

        # Create results section
        self._create_results_section()

    def _create_header(self):
        """Create the header section."""
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill=tk.X, pady=(0, 20))

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Instagram Memory Book Generator",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=10)

        # Subtitle
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Transform your Instagram data exports into beautiful memory books",
            font=ctk.CTkFont(size=14)
        )
        subtitle_label.pack(pady=(0, 10))

    def _create_folder_selection(self):
        """Create the folder selection section."""
        folder_frame = ctk.CTkFrame(self.main_frame)
        folder_frame.pack(fill=tk.X, pady=10)

        # Section title
        section_label = ctk.CTkLabel(
            folder_frame,
            text="Step 1: Select Instagram Data Folder",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        section_label.pack(fill=tk.X, padx=15, pady=(15, 5))

        # Description
        description_label = ctk.CTkLabel(
            folder_frame,
            text="Select the folder containing your Instagram data export",
            anchor="w"
        )
        description_label.pack(fill=tk.X, padx=15, pady=(0, 10))

        # Folder selection
        folder_select_frame = ctk.CTkFrame(folder_frame, fg_color="transparent")
        folder_select_frame.pack(fill=tk.X, padx=15, pady=5)

        folder_entry = ctk.CTkEntry(
            folder_select_frame,
            textvariable=self.folder_path,
            placeholder_text="Instagram data folder path",
            height=35
        )
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        browse_button = ctk.CTkButton(
            folder_select_frame,
            text="Browse",
            command=self._browse_folder,
            width=100,
            height=35
        )
        browse_button.pack(side=tk.RIGHT)

        # Files found section
        self.files_frame = ctk.CTkFrame(folder_frame, fg_color="transparent")
        self.files_frame.pack(fill=tk.X, padx=15, pady=10)

        self.files_label = ctk.CTkLabel(
            self.files_frame,
            text="No files detected yet",
            anchor="w"
        )
        self.files_label.pack(fill=tk.X)

    def _create_user_input(self):
        """Create the user input section."""
        user_frame = ctk.CTkFrame(self.main_frame)
        user_frame.pack(fill=tk.X, pady=10)

        # Section title
        section_label = ctk.CTkLabel(
            user_frame,
            text="Step 2: Enter User Information",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        section_label.pack(fill=tk.X, padx=15, pady=(15, 5))

        # User input fields
        input_frame = ctk.CTkFrame(user_frame, fg_color="transparent")
        input_frame.pack(fill=tk.X, padx=15, pady=10)

        # Target user
        target_label = ctk.CTkLabel(
            input_frame,
            text="Friend/Group Name:",
            anchor="w",
            width=150
        )
        target_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        target_entry = ctk.CTkEntry(
            input_frame,
            textvariable=self.target_user,
            placeholder_text="Enter friend's username or group name",
            width=200,
            height=35
        )
        target_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # My name
        my_name_label = ctk.CTkLabel(
            input_frame,
            text="Your Username:",
            anchor="w",
            width=150
        )
        my_name_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        my_name_entry = ctk.CTkEntry(
            input_frame,
            textvariable=self.my_name,
            placeholder_text="Enter your username",
            width=200,
            height=35
        )
        my_name_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Output path
        output_label = ctk.CTkLabel(
            input_frame,
            text="Output Folder:",
            anchor="w",
            width=150
        )
        output_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)

        output_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        output_frame.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        output_entry = ctk.CTkEntry(
            output_frame,
            textvariable=self.output_path,
            placeholder_text="Output folder path",
            height=35
        )
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        output_button = ctk.CTkButton(
            output_frame,
            text="Browse",
            command=self._browse_output_folder,
            width=80,
            height=35
        )
        output_button.pack(side=tk.RIGHT)

        # Group chat checkbox
        group_chat_label = ctk.CTkLabel(
            input_frame,
            text="Group Chat:",
            anchor="w",
            width=150
        )
        group_chat_label.grid(row=3, column=0, sticky="w", padx=5, pady=5)

        group_chat_checkbox = ctk.CTkCheckBox(
            input_frame,
            text="This is a group conversation",
            variable=self.is_group_chat,
            onvalue=True,
            offvalue=False
        )
        group_chat_checkbox.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        # Configure grid
        input_frame.columnconfigure(1, weight=1)

    def _create_custom_words_input(self):
        """Create the custom words input section."""
        words_frame = ctk.CTkFrame(self.main_frame)
        words_frame.pack(fill=tk.X, pady=10)

        # Section title
        section_label = ctk.CTkLabel(
            words_frame,
            text="Step 3: Custom Words/Emojis to Count (Optional)",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        section_label.pack(fill=tk.X, padx=15, pady=(15, 5))

        # Description
        description_label = ctk.CTkLabel(
            words_frame,
            text="Enter words or emojis to count, separated by commas (e.g., 'love, 😊, thanks')",
            anchor="w"
        )
        description_label.pack(fill=tk.X, padx=15, pady=(0, 10))

        # Custom words entry
        custom_entry = ctk.CTkEntry(
            words_frame,
            textvariable=self.custom_words,
            placeholder_text="Enter custom words or emojis to count",
            height=35
        )
        custom_entry.pack(fill=tk.X, padx=15, pady=5)

    def _create_analyze_button(self):
        """Create the analyze button section."""
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(fill=tk.X, pady=15)

        self.analyze_button = ctk.CTkButton(
            button_frame,
            text="Analyze Conversations",
            command=self._start_analysis,
            height=40,
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.analyze_button.pack(padx=100)

    def _create_progress_section(self):
        """Create the progress section."""
        self.progress_frame = ctk.CTkFrame(self.main_frame)
        self.progress_frame.pack(fill=tk.X, pady=10)
        self.progress_frame.pack_forget()  # Hide initially

        # Progress label
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="Analyzing conversations...",
            font=ctk.CTkFont(size=14)
        )
        self.progress_label.pack(pady=(15, 5))

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, width=400)
        self.progress_bar.pack(pady=(5, 15))
        self.progress_bar.set(0)

    def _create_results_section(self):
        """Create the results section."""
        self.results_frame = ctk.CTkFrame(self.main_frame)
        self.results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.results_frame.pack_forget()  # Hide initially

        # Results title
        results_title = ctk.CTkLabel(
            self.results_frame,
            text="Analysis Results",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        results_title.pack(pady=(15, 10))

        # Results text
        self.results_text = ctk.CTkTextbox(self.results_frame, wrap="word")
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))

        # Buttons frame
        buttons_frame = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        buttons_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        # Open results folder button
        self.open_folder_button = ctk.CTkButton(
            buttons_frame,
            text="Open Results Folder",
            command=self._open_results_folder,
            height=35
        )
        self.open_folder_button.pack(side=tk.LEFT, padx=5)

        # New analysis button
        self.new_analysis_button = ctk.CTkButton(
            buttons_frame,
            text="Start New Analysis",
            command=self._reset_ui,
            height=35
        )
        self.new_analysis_button.pack(side=tk.RIGHT, padx=5)

    def _browse_folder(self):
        """Open folder browser dialog."""
        folder_selected = filedialog.askdirectory(title="Select Instagram Data Folder")
        if folder_selected:
            self.folder_path.set(folder_selected)
            self._scan_folder()

    def _browse_output_folder(self):
        """Open output folder browser dialog."""
        folder_selected = filedialog.askdirectory(title="Select Output Folder")
        if folder_selected:
            self.output_path.set(folder_selected)

    def _scan_folder(self):
        """Scan the selected folder for JSON files and detect participants."""
        folder_path = self.folder_path.get()
        if not folder_path or not os.path.isdir(folder_path):
            return

        # Find all JSON files
        self.json_files = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.json'):
                    self.json_files.append(os.path.join(root, file))

        # Validate JSON files for chat content
        self.valid_json_files = []
        all_participants = set()

        for file_path in self.json_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'messages' in data and isinstance(data['messages'], list):
                        # Check if messages have required fields
                        if data['messages'] and all(
                            'sender_name' in msg and 'timestamp_ms' in msg
                            for msg in data['messages'][:5]  # Check first 5 messages
                        ):
                            self.valid_json_files.append(file_path)

                            # Collect all unique participants
                            for msg in data['messages']:
                                if 'sender_name' in msg and msg['sender_name']:
                                    # Fix any broken text in sender name
                                    sender = utils.fix_broken_text(msg['sender_name'])
                                    all_participants.add(sender)
            except (json.JSONDecodeError, UnicodeDecodeError, IOError):
                # Skip invalid files
                continue

        # Update UI
        if self.valid_json_files:
            self.files_label.configure(
                text=f"Found {len(self.valid_json_files)} valid conversation file(s) out of {len(self.json_files)} JSON file(s)"
            )

            # Auto-detect participants
            if len(all_participants) == 2:
                # If exactly two participants, assume one is the user and one is the friend
                participants = list(all_participants)

                # Try to determine which one is the user based on folder name
                folder_name = os.path.basename(folder_path).lower()

                # If folder contains "instagram" and a username, that's likely the user
                user_detected = False
                for participant in participants:
                    if participant.lower() in folder_name:
                        self.my_name.set(participant)
                        self.target_user.set([p for p in participants if p != participant][0])
                        user_detected = True
                        break

                # If we couldn't determine, just set them in order
                if not user_detected:
                    self.my_name.set(participants[0])
                    self.target_user.set(participants[1])

                self.files_label.configure(
                    text=f"Found {len(self.valid_json_files)} valid conversation file(s). Auto-detected participants: {', '.join(participants)}"
                )
            elif len(all_participants) > 2:
                # If more than two participants, it's a group chat
                self.files_label.configure(
                    text=f"Found {len(self.valid_json_files)} valid conversation file(s) with {len(all_participants)} participants. Please enter the main participants manually."
                )
        else:
            self.files_label.configure(
                text="No valid conversation files found. Please select a different folder."
            )

    def _start_analysis(self):
        """Start the analysis process."""
        # Validate inputs
        if not self.valid_json_files:
            self._show_error("No valid conversation files found. Please select a different folder.")
            return

        if not self.target_user.get():
            self._show_error("Please enter your friend's username.")
            return

        if not self.my_name.get():
            self._show_error("Please enter your username.")
            return

        if not self.output_path.get():
            self._show_error("Please select an output folder.")
            return

        # Show progress UI
        self.analyze_button.configure(state="disabled")
        self.progress_frame.pack(fill=tk.X, pady=10, after=self.analyze_button.winfo_parent())
        self.progress_bar.set(0)
        self.update_idletasks()

        # Start analysis in a separate thread
        self.is_analyzing = True
        threading.Thread(target=self._run_analysis, daemon=True).start()
        self._update_progress_animation()

    def _run_analysis(self):
        """Run the analysis process in a background thread."""
        try:
            # Create output directories
            output_dirs = utils.setup_directories(self.output_path.get())

            # Initialize processor
            processor = InstagramDataProcessor(
                self.folder_path.get(),
                self.target_user.get(),
                self.my_name.get(),
                is_group_chat=self.is_group_chat.get()
            )

            # Process JSON files
            messages = processor.process_json_files()

            # Generate statistics
            stats = processor.get_conversation_stats()

            # Extract media files
            media_extractor = MediaExtractor(
                self.folder_path.get(),
                self.output_path.get(),
                self.target_user.get()
            )
            media_stats = media_extractor.extract_all_media(messages)

            # Process custom words if provided
            custom_word_counts = {}
            if self.custom_words.get():
                custom_words = [word.strip() for word in self.custom_words.get().split(',')]
                for word in custom_words:
                    if word:
                        count = sum(1 for msg in messages if word in msg.get('content', ''))
                        custom_word_counts[word] = count

            # Export to TXT
            txt_exporter = TxtExporter(output_dirs["text"])
            txt_file = txt_exporter.export(messages, self.target_user.get(), self.my_name.get(), stats)

            # Export to HTML
            html_exporter = HTMLExporter(output_dirs["html"])
            html_file = html_exporter.export(
                messages,
                self.target_user.get(),
                self.my_name.get(),
                stats,
                is_group_chat=self.is_group_chat.get()
            )

            # Export to PDF
            pdf_exporter = PDFExporter(output_dirs["pdf"])
            pdf_file = pdf_exporter.export(
                messages,
                self.target_user.get(),
                self.my_name.get(),
                stats,
                is_group_chat=self.is_group_chat.get()
            )

            # Export to Excel
            excel_exporter = ExcelExporter(output_dirs["excel"])
            excel_file = excel_exporter.export(
                messages,
                self.target_user.get(),
                self.my_name.get(),
                stats,
                is_group_chat=self.is_group_chat.get()
            )

            # Store results
            self.analysis_results = {
                'messages': len(messages),
                'stats': stats,
                'media_stats': media_stats,
                'custom_word_counts': custom_word_counts,
                'output_files': {
                    'txt': txt_file,
                    'html': html_file,
                    'pdf': pdf_file,
                    'excel': excel_file
                },
                'output_path': self.output_path.get()
            }

            # Mark analysis as complete
            self.is_analyzing = False
            self.analysis_complete = True

        except Exception as e:
            self.is_analyzing = False
            self.analysis_complete = False
            self.analysis_error = str(e)

    def _update_progress_animation(self):
        """Update the progress animation."""
        if self.is_analyzing:
            # Update progress bar with animation
            progress = self.progress_bar.get()
            if progress >= 1.0:
                progress = 0.0
            else:
                progress += 0.01
            self.progress_bar.set(progress)

            # Schedule next update
            self.after(50, self._update_progress_animation)
        elif self.analysis_complete:
            # Analysis completed successfully
            self.progress_bar.set(1.0)
            self.progress_label.configure(text="Analysis completed successfully!")
            self.after(1000, self._show_results)
        else:
            # Analysis failed
            self.progress_bar.set(0)
            self.progress_label.configure(text=f"Analysis failed: {self.analysis_error}")
            self.analyze_button.configure(state="normal")

    def _show_results(self):
        """Show the analysis results."""
        # Hide progress frame
        self.progress_frame.pack_forget()

        # Show results frame
        self.results_frame.pack(fill=tk.BOTH, expand=True, pady=10, after=self.analyze_button.winfo_parent())

        # Format results text
        results = self.analysis_results
        stats = results['stats']
        media_stats = results['media_stats']

        # Clear previous results
        self.results_text.delete("0.0", "end")

        # Add results text
        self.results_text.insert("end", "📊 CONVERSATION ANALYSIS RESULTS 📊\n\n", "heading")

        # Basic stats
        self.results_text.insert("end", "📝 Basic Statistics:\n", "subheading")
        self.results_text.insert("end", f"• Total Messages: {results['messages']}\n")

        # Check if it's a group chat
        if stats.get('is_group_chat', False):
            self.results_text.insert("end", f"• Group Chat: Yes (with {stats['participants_count']} participants)\n")
            self.results_text.insert("end", f"• Messages from {self.my_name.get()}: {stats['messages_by_sender'].get(self.my_name.get(), 0)}\n")

            # Show top 5 most active participants
            if 'most_active_participants' in stats:
                self.results_text.insert("end", "• Most Active Participants:\n")
                for i, (participant, count) in enumerate(stats['most_active_participants'][:5]):
                    self.results_text.insert("end", f"  {i+1}. {participant}: {count} messages\n")
        else:
            self.results_text.insert("end", f"• Messages from {self.my_name.get()}: {stats['messages_by_sender'].get(self.my_name.get(), 0)}\n")
            self.results_text.insert("end", f"• Messages from {self.target_user.get()}: {stats['messages_by_sender'].get(self.target_user.get(), 0)}\n")

        self.results_text.insert("end", f"• Total Emojis: {stats['total_emojis']}\n")
        self.results_text.insert("end", f"• Conversation Duration: {stats['conversation_duration_days']} days\n")
        self.results_text.insert("end", f"• First Message Date: {stats['first_message_date']}\n")
        self.results_text.insert("end", f"• Last Message Date: {stats['last_message_date']}\n")
        self.results_text.insert("end", f"• Most Active Day: {stats['most_active_day']} ({stats['most_active_day_count']} messages)\n\n")

        # Media stats
        self.results_text.insert("end", "📷 Media Statistics:\n", "subheading")
        self.results_text.insert("end", f"• Photos: {media_stats['photos']}\n")
        self.results_text.insert("end", f"• Videos: {media_stats['videos']}\n")
        self.results_text.insert("end", f"• Audio Files: {media_stats['audio']}\n\n")

        # Custom word counts
        if results['custom_word_counts']:
            self.results_text.insert("end", "🔍 Custom Word/Emoji Counts:\n", "subheading")
            for word, count in results['custom_word_counts'].items():
                self.results_text.insert("end", f"• '{word}': {count} occurrences\n")
            self.results_text.insert("end", "\n")

        # Output files
        self.results_text.insert("end", "📁 Output Files:\n", "subheading")
        if results['output_files']['txt']:
            self.results_text.insert("end", f"• TXT: {os.path.basename(results['output_files']['txt'])}\n")
        if results['output_files']['html']:
            self.results_text.insert("end", f"• HTML: {os.path.basename(results['output_files']['html'])}\n")
        if results['output_files']['pdf']:
            self.results_text.insert("end", f"• PDF: {os.path.basename(results['output_files']['pdf'])}\n")
        if results['output_files']['excel']:
            self.results_text.insert("end", f"• Excel: {os.path.basename(results['output_files']['excel'])}\n")
        self.results_text.insert("end", f"\nAll files saved to: {results['output_path']}\n")

        # Configure text tags
        self.results_text.tag_configure("heading", font=ctk.CTkFont(size=16, weight="bold"))
        self.results_text.tag_configure("subheading", font=ctk.CTkFont(size=14, weight="bold"))

    def _open_results_folder(self):
        """Open the results folder in file explorer."""
        if self.analysis_results and 'output_path' in self.analysis_results:
            folder_path = self.analysis_results['output_path']
            if os.path.exists(folder_path):
                # Open folder using the default file explorer
                try:
                    # On Windows, use os.startfile
                    os.startfile(folder_path)
                except Exception as e:
                    print(f"Error opening folder: {e}")

    def _reset_ui(self):
        """Reset the UI for a new analysis."""
        # Hide results frame
        self.results_frame.pack_forget()

        # Reset state variables
        self.is_analyzing = False
        self.analysis_complete = False
        self.analysis_results = None

        # Enable analyze button
        self.analyze_button.configure(state="normal")

    def _show_error(self, message):
        """Show an error message dialog."""
        error_window = ctk.CTkToplevel(self)
        error_window.title("Error")
        error_window.geometry("400x150")
        error_window.resizable(False, False)
        error_window.grab_set()  # Make the window modal

        # Center the window
        error_window.update_idletasks()
        width = error_window.winfo_width()
        height = error_window.winfo_height()
        x = (error_window.winfo_screenwidth() // 2) - (width // 2)
        y = (error_window.winfo_screenheight() // 2) - (height // 2)
        error_window.geometry(f"{width}x{height}+{x}+{y}")

        # Error message
        error_label = ctk.CTkLabel(
            error_window,
            text=message,
            wraplength=350
        )
        error_label.pack(pady=(20, 10), padx=20)

        # OK button
        ok_button = ctk.CTkButton(
            error_window,
            text="OK",
            command=error_window.destroy,
            width=100
        )
        ok_button.pack(pady=(0, 20))

def main():
    """Run the GUI application."""
    app = InstagramDataProcessorApp()
    app.mainloop()

if __name__ == "__main__":
    main()
