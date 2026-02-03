import sys
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QMessageBox, 
                             QFileDialog, QListWidget, QHBoxLayout, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Global Config
API_URL = "http://127.0.0.1:8000/api"

class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setWindowTitle("Login - Chemical Visualizer")
        self.resize(300, 200)
        
        layout = QVBoxLayout()
        
        self.username = QLineEdit(self)
        self.username.setPlaceholderText("Username")
        layout.addWidget(self.username)
        
        self.password = QLineEdit(self)
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)
        
        btn = QPushButton("Login", self)
        btn.clicked.connect(self.handle_login)
        layout.addWidget(btn)
        
        self.setLayout(layout)

    def handle_login(self):
        username = self.username.text()
        password = self.password.text()
        
        try:
            resp = requests.post(f"{API_URL}/login/", json={'username': username, 'password': password})
            if resp.status_code == 200:
                token = resp.json()['token']
                self.on_login_success(token)
                self.close()
            else:
                QMessageBox.warning(self, "Error", "Invalid Credentials")
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", str(e))


class DashboardWindow(QMainWindow):
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.headers = {'Authorization': f'Token {self.token}'}
        self.setWindowTitle("Chemical Equipment Dashboard (Desktop)")
        self.resize(1000, 700)
        
        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Sidebar (History + Upload)
        sidebar_layout = QVBoxLayout()
        
        self.upload_btn = QPushButton("Upload New CSV")
        self.upload_btn.clicked.connect(self.upload_file)
        sidebar_layout.addWidget(self.upload_btn)
        
        sidebar_layout.addWidget(QLabel("Recent Uploads:"))
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.load_analytics)
        sidebar_layout.addWidget(self.history_list)
        
        self.pdf_btn = QPushButton("Download PDF")
        self.pdf_btn.clicked.connect(self.download_pdf)
        self.pdf_btn.setEnabled(False)
        sidebar_layout.addWidget(self.pdf_btn)
        
        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar_layout)
        sidebar_widget.setMaximumWidth(250)
        main_layout.addWidget(sidebar_widget)
        
        # Content Area (Charts + Stats)
        content_layout = QVBoxLayout()
        
        self.stats_label = QLabel("Select a file to view statistics")
        content_layout.addWidget(self.stats_label)
        
        # Matplotlib Chart 
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        content_layout.addWidget(self.canvas)
        
        # Data Table
        self.table = QTableWidget()
        content_layout.addWidget(self.table)
        
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget)
        
        # Initial Load
        self.refresh_history()
        self.current_file_id = None

    def refresh_history(self):
        try:
            resp = requests.get(f"{API_URL}/files/", headers=self.headers)
            if resp.status_code == 200:
                self.history_list.clear()
                self.files = resp.json()
                for f in self.files:
                    self.history_list.addItem(f"{f['filename']} ({f['uploaded_at'][:10]})")
        except:
            pass

    def upload_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open CSV', '.', "CSV Files (*.csv)")
        if fname:
            files = {'file': open(fname, 'rb')}
            try:
                resp = requests.post(f"{API_URL}/files/", files=files, headers=self.headers)
                if resp.status_code == 201:
                    QMessageBox.information(self, "Success", "File Uploaded")
                    self.refresh_history()
                else:
                    QMessageBox.warning(self, "Error", "Upload Failed")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def load_analytics(self, item):
        idx = self.history_list.row(item)
        file_id = self.files[idx]['id']
        self.current_file_id = file_id
        
        try:
            resp = requests.get(f"{API_URL}/analytics/{file_id}/", headers=self.headers)
            if resp.status_code == 200:
                data = resp.json()
                
                # Update Text Stats
                stats_text = (f"File: {data['filename']} | Total: {data['total_count']} | "
                              f"Avg Temp: {data['averages'].get('Temperature', 0):.2f}")
                self.stats_label.setText(stats_text)
                
                # Update Chart (Matplotlib)
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                types = list(data['type_distribution'].keys())
                counts = list(data['type_distribution'].values())
                ax.bar(types, counts, color='skyblue')
                ax.set_title("Equipment Type Distribution")
                self.canvas.draw()
                
                # Update Table
                preview = data['preview']
                if preview:
                    headers = list(preview[0].keys())
                    self.table.setColumnCount(len(headers))
                    self.table.setRowCount(len(preview))
                    self.table.setHorizontalHeaderLabels(headers)
                    for i, row in enumerate(preview):
                        for j, (key, val) in enumerate(row.items()):
                            self.table.setItem(i, j, QTableWidgetItem(str(val)))
                
                self.pdf_btn.setEnabled(True)
        except Exception as e:
            print(e)

    def download_pdf(self):
        if self.current_file_id:
            try:
                resp = requests.get(f"{API_URL}/pdf/{self.current_file_id}/", headers=self.headers)
                if resp.status_code == 200:
                    save_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "report.pdf", "PDF Files (*.pdf)")
                    if save_path:
                        with open(save_path, 'wb') as f:
                            f.write(resp.content)
                        QMessageBox.information(self, "Success", "PDF Saved")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Logic to switch windows
    def start_dashboard(token):
        global dashboard
        dashboard = DashboardWindow(token)
        dashboard.show()
    
    login = LoginWindow(start_dashboard)
    login.show()
    
    sys.exit(app.exec_())