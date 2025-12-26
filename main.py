"""
Main application GUI for MP3 Vocabulary Generator.
A desktop application for generating MP3 lessons from Czech-English word pairs.
"""

import sys
from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLabel, QPushButton, QFileDialog, QDoubleSpinBox,
    QMessageBox, QGroupBox, QFormLayout, QStatusBar, QSplashScreen
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor

from tts_engine import TTSEngine, setup_ffmpeg_path
from utils import parse_word_pairs, validate_pause_duration, check_ffmpeg_available, check_local_ffmpeg


class GenerationThread(QThread):
    """Worker thread for audio generation to keep UI responsive."""
    
    finished = Signal(str)  # Success message
    error = Signal(str)  # Error message
    progress = Signal(str)  # Progress message
    
    def __init__(self, word_pairs, pause_within, pause_between, output_path):
        super().__init__()
        self.word_pairs = word_pairs
        self.pause_within = pause_within
        self.pause_between = pause_between
        self.output_path = output_path
    
    def run(self):
        """Run the audio generation in background thread."""
        try:
            engine = TTSEngine()
            engine.generate_lesson_audio(
                self.word_pairs,
                self.pause_within,
                self.pause_between,
                self.output_path,
                progress_callback=lambda msg: self.progress.emit(msg)
            )
            self.finished.emit(f"Successfully generated MP3: {self.output_path}")
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.output_path: Optional[Path] = None
        self.generation_thread: Optional[GenerationThread] = None
        self.init_ui()
        self.check_ffmpeg_on_startup()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("MP3 Vocabulary Generator")
        self.setMinimumSize(700, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("MP3 Vocabulary Generator")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Word pairs input section
        pairs_group = QGroupBox("Word Pairs Input")
        pairs_layout = QVBoxLayout()
        
        pairs_label = QLabel("Enter one pair per line: Czech,English")
        pairs_layout.addWidget(pairs_label)
        
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(
            "Enter one pair per line: Czech,English\n\n"
            "Example:\n"
            "pes,dog\n"
            "kočka,cat\n"
            "dům,house\n"
            "auto,car\n"
            "kniha,book\n"
            "stůl,table\n"
            "židle,chair\n"
            "okno,window\n"
            "dveře,door\n"
            "střecha,roof"
        )
        self.text_input.setMinimumHeight(200)
        pairs_layout.addWidget(self.text_input)
        
        pairs_group.setLayout(pairs_layout)
        main_layout.addWidget(pairs_group)
        
        # Pause settings section
        pause_group = QGroupBox("Pause Settings")
        pause_layout = QFormLayout()
        
        self.pause_within_spinbox = QDoubleSpinBox()
        self.pause_within_spinbox.setRange(0.0, 10.0)
        self.pause_within_spinbox.setSingleStep(0.1)
        self.pause_within_spinbox.setValue(1.1)
        self.pause_within_spinbox.setSuffix(" seconds")
        self.pause_within_spinbox.setDecimals(1)
        pause_layout.addRow("Pause within pair (Czech → English):", self.pause_within_spinbox)
        
        self.pause_between_spinbox = QDoubleSpinBox()
        self.pause_between_spinbox.setRange(0.0, 10.0)
        self.pause_between_spinbox.setSingleStep(0.1)
        self.pause_between_spinbox.setValue(1.7)
        self.pause_between_spinbox.setSuffix(" seconds")
        self.pause_between_spinbox.setDecimals(1)
        pause_layout.addRow("Pause between pairs:", self.pause_between_spinbox)
        
        pause_group.setLayout(pause_layout)
        main_layout.addWidget(pause_group)
        
        # Output file section
        output_group = QGroupBox("Output File")
        output_layout = QVBoxLayout()
        
        output_file_layout = QHBoxLayout()
        self.output_label = QLabel("No file selected")
        self.output_label.setStyleSheet("color: gray;")
        output_file_layout.addWidget(self.output_label)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_output_file)
        output_file_layout.addWidget(self.browse_button)
        
        output_layout.addLayout(output_file_layout)
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)
        
        # Generate button
        self.generate_button = QPushButton("Generate MP3")
        self.generate_button.setMinimumHeight(40)
        generate_font = QFont()
        generate_font.setPointSize(12)
        generate_font.setBold(True)
        self.generate_button.setFont(generate_font)
        self.generate_button.clicked.connect(self.generate_mp3)
        main_layout.addWidget(self.generate_button)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Add stretch to push everything to top
        main_layout.addStretch()
    
    def browse_output_file(self):
        """Open file dialog to select output MP3 file location."""
        default_path = Path.home() / "Desktop" / "vocabulary_lesson.mp3"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save MP3 File",
            str(default_path),
            "MP3 Files (*.mp3);;All Files (*)"
        )
        
        if file_path:
            self.output_path = Path(file_path)
            self.output_label.setText(str(self.output_path))
            self.output_label.setStyleSheet("color: black;")
    
    def check_ffmpeg_on_startup(self):
        """Check for ffmpeg availability when application starts."""
        # Determine base path (executable location or script location)
        if getattr(sys, 'frozen', False):
            exe_path = Path(sys.executable)
            base_path = exe_path.parent
        else:
            base_path = Path(__file__).parent
        
        # Try to setup local ffmpeg
        local_ffmpeg_setup = setup_ffmpeg_path()
        local_available, local_path = check_local_ffmpeg()
        
        if not local_available and not local_ffmpeg_setup:
            # FFmpeg is required - show error and close
            expected_path = base_path / "ffmpeg" / "bin" / "ffmpeg.exe"
            QMessageBox.critical(
                self,
                "FFmpeg Required",
                "FFmpeg not found!\n\n"
                f"Please place ffmpeg in the following location:\n"
                f"{expected_path.parent}\n\n"
                f"Expected file: {expected_path}\n\n"
                "Download ffmpeg from: https://www.gyan.dev/ffmpeg/builds/\n"
                "Extract the 'bin' folder contents to the 'ffmpeg/bin' folder\n"
                "next to this executable.\n\n"
                "The application will now close."
            )
            self.status_bar.showMessage("Error: FFmpeg not found")
            # Close the application
            self.close()
            return
        
        # FFmpeg found
        if local_path:
            self.status_bar.showMessage(f"Using local ffmpeg: {local_path.parent}")
        else:
            self.status_bar.showMessage("Using local ffmpeg (configured)")
    
    def generate_mp3(self):
        """Generate MP3 lesson from word pairs."""
        # Determine base path
        if getattr(sys, 'frozen', False):
            exe_path = Path(sys.executable)
            base_path = exe_path.parent
        else:
            base_path = Path(__file__).parent
        
        # Try to setup local ffmpeg
        local_ffmpeg_setup = setup_ffmpeg_path()
        local_available, local_path = check_local_ffmpeg()
        
        if not local_available and not local_ffmpeg_setup:
            # FFmpeg is required
            expected_path = base_path / "ffmpeg" / "bin" / "ffmpeg.exe"
            QMessageBox.critical(
                self,
                "FFmpeg Required",
                "FFmpeg not found!\n\n"
                f"Please place ffmpeg in:\n{expected_path.parent}\n\n"
                f"Expected file: {expected_path}\n\n"
                "Download from: https://www.gyan.dev/ffmpeg/builds/"
            )
            return
        
        # Validate output path
        if not self.output_path:
            QMessageBox.warning(
                self,
                "Output File Required",
                "Please select an output MP3 file location."
            )
            return
        
        # Parse word pairs
        try:
            text = self.text_input.toPlainText()
            word_pairs = parse_word_pairs(text)
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", str(e))
            return
        
        # Get pause durations
        pause_within = self.pause_within_spinbox.value()
        pause_between = self.pause_between_spinbox.value()
        
        # Validate pause durations
        pause_within = validate_pause_duration(pause_within)
        pause_between = validate_pause_duration(pause_between)
        
        # Disable UI during generation
        self.generate_button.setEnabled(False)
        self.browse_button.setEnabled(False)
        self.text_input.setEnabled(False)
        self.pause_within_spinbox.setEnabled(False)
        self.pause_between_spinbox.setEnabled(False)
        
        # Update status
        self.status_bar.showMessage("Generating MP3... Please wait.")
        
        # Create and start generation thread
        self.generation_thread = GenerationThread(
            word_pairs,
            pause_within,
            pause_between,
            self.output_path
        )
        self.generation_thread.progress.connect(self.update_status)
        self.generation_thread.finished.connect(self.on_generation_finished)
        self.generation_thread.error.connect(self.on_generation_error)
        self.generation_thread.start()
    
    def update_status(self, message: str):
        """Update status bar with progress message."""
        self.status_bar.showMessage(message)
    
    def on_generation_finished(self, message: str):
        """Handle successful generation completion."""
        self.status_bar.showMessage(message)
        QMessageBox.information(self, "Success", message)
        self.enable_ui()
    
    def on_generation_error(self, error_message: str):
        """Handle generation error."""
        self.status_bar.showMessage(f"Error: {error_message}")
        
        # Check if it's an ffmpeg-related error
        error_lower = error_message.lower()
        if "winerror 2" in error_lower or "cannot find" in error_lower or "ffmpeg" in error_lower:
            ffmpeg_available, ffmpeg_error_msg = check_ffmpeg_available()
            if not ffmpeg_available:
                error_message = f"{error_message}\n\n{ffmpeg_error_msg}"
        
        QMessageBox.critical(self, "Generation Failed", f"An error occurred:\n\n{error_message}")
        self.enable_ui()
    
    def enable_ui(self):
        """Re-enable UI controls after generation."""
        self.generate_button.setEnabled(True)
        self.browse_button.setEnabled(True)
        self.text_input.setEnabled(True)
        self.pause_within_spinbox.setEnabled(True)
        self.pause_between_spinbox.setEnabled(True)
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.generation_thread and self.generation_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "Generation in Progress",
                "Audio generation is in progress. Do you want to cancel and exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.generation_thread.terminate()
                self.generation_thread.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    """Main entry point with splash screen."""

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Create splash pixmap
    width, height = 400, 200
    splash_pix = QPixmap(width, height)
    splash_pix.fill(Qt.transparent)
    
    # Draw rounded semi-transparent background
    painter = QPainter(splash_pix)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor(30, 30, 30, 190))  # dark translucent
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(0, 0, width, height, 20, 20)
    painter.end()

    splash = QSplashScreen(splash_pix)
    splash.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)
    splash.setAttribute(Qt.WA_TranslucentBackground)
    splash.setFont(QFont("Arial", 20, QFont.Bold))

    # Animated loading text
    base_text = "Loading"
    dots_state = {"count": 0}

    def update_loading_text():
        dots_state["count"] = (dots_state["count"] + 1) % 4
        text = base_text + "." * dots_state["count"]
        splash.showMessage(
            text,
            Qt.AlignCenter,
            Qt.white
        )

    loading_timer = QTimer()
    loading_timer.timeout.connect(update_loading_text)
    loading_timer.start(300)

    update_loading_text()
    splash.show()
    app.processEvents()

    # Simulate loading (or do real init)
    def start_main_window():
        loading_timer.stop()
        app.main_window = MainWindow()
        app.main_window.show()
        splash.finish(app.main_window)

    # The delay can be reduced if MainWindow loads quickly.
    QTimer.singleShot(800, start_main_window)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
