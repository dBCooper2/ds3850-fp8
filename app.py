import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                            QLineEdit, QTextEdit, QPushButton, QVBoxLayout, 
                            QHBoxLayout, QMessageBox, QInputDialog)
from PyQt6.QtCore import Qt
import sqlite3
import re

class FeedbackApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Customer Feedback System")
        self.setMinimumSize(600, 600)
        
        # Database initialization
        self.setup_database()
        
        # Password for admin access
        self.ADMIN_PASSWORD = "password"
        
        # Create and set the central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create the main layout
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Add title
        title_label = QLabel("Customer Feedback Form")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Add form elements
        layout.addWidget(QLabel("Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter Your Name")
        layout.addWidget(self.name_input)
        
        layout.addWidget(QLabel("Email:"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter Your Email")
        layout.addWidget(self.email_input)
        
        layout.addWidget(QLabel("Feedback:"))
        self.feedback_input = QTextEdit()
        self.feedback_input.setPlaceholderText("Enter Your Feedback Here...")
        layout.addWidget(self.feedback_input)
        
        # Create button layout
        button_layout = QHBoxLayout()
        
        # Add buttons
        submit_btn = QPushButton("Submit Feedback")
        submit_btn.clicked.connect(self.submit_feedback)
        button_layout.addWidget(submit_btn)
        
        view_btn = QPushButton("View All Feedback")
        view_btn.clicked.connect(self.view_feedback)
        button_layout.addWidget(view_btn)
        
        clear_btn = QPushButton("Clear Form")
        clear_btn.clicked.connect(self.clear_form)
        button_layout.addWidget(clear_btn)
        
        # Add button layout to main layout
        layout.addLayout(button_layout)
        
        # Show the window
        self.show()
    
    def setup_database(self):
        """Initialize SQLite database and create table if it doesn't exist"""
        try:
            self.conn = sqlite3.connect('responses.db')
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    feedback TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", 
                               f"Failed to initialize database: {str(e)}")
    
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def submit_feedback(self):
        """Submit feedback to database"""
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        feedback = self.feedback_input.toPlainText().strip()
        
        # Validate input
        if not all([name, email, feedback]):
            QMessageBox.warning(self, "ERROR!", "All fields are required!")
            return
        
        if not self.validate_email(email):
            QMessageBox.warning(self, "ERROR!", "Please enter a valid email address!")
            return
        
        try:
            self.cursor.execute('''
                INSERT INTO feedback (name, email, feedback)
                VALUES (?, ?, ?)
            ''', (name, email, feedback))
            self.conn.commit()
            QMessageBox.information(self, "Success", "Feedback submitted successfully!")
            self.clear_form()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "ERROR!", f"Failed to submit feedback: {str(e)}")
    
    def view_feedback(self):
        """Display all feedback (password protected)"""
        password, ok = QInputDialog.getText(
            self, "Password Required", "Enter Root Password:",
            QLineEdit.EchoMode.Password
        )
        
        if not ok:
            return
        
        if password != self.ADMIN_PASSWORD:
            QMessageBox.warning(self, "ERROR!", "Incorrect password!")
            return
        
        try:
            self.cursor.execute('SELECT * FROM feedback ORDER BY timestamp DESC')
            records = self.cursor.fetchall()
            
            if not records:
                print("\nNo feedback entries found.")
                return
            
            print("\n=== All Feedback Entries ===")
            for record in records:
                print(f"\nID: {record[0]}")
                print(f"Name: {record[1]}")
                print(f"Email: {record[2]}")
                print(f"Feedback: {record[3]}")
                print(f"Timestamp: {record[4]}")
                print("-" * 50)
                
        except sqlite3.Error as e:
            QMessageBox.critical(self, "ERROR!", f"Failed to retrieve feedback: {str(e)}")
    
    def clear_form(self):
        """Clear all input fields"""
        self.name_input.clear()
        self.email_input.clear()
        self.feedback_input.clear()
    
    def closeEvent(self, event):
        """Handle application closure"""
        if hasattr(self, 'conn'):
            self.conn.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Breeze')
    
    # Create and show the main window
    window = FeedbackApp()
    
    # Start the event loop
    sys.exit(app.exec())