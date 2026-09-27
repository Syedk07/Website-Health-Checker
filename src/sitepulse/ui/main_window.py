"""
Main application window for SitePulse.
"""

import tkinter as tk
from tkinter import ttk

from ..database import DatabaseManager
from ..services import WebsiteService, HealthChecker, ReportService
from .dashboard import DashboardView
from .websites import WebsitesView
from .history import HistoryView
from .reports import ReportsView


class MainWindow:
    """Main application window."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize the main window."""
        self.root = tk.Tk()
        self.root.title("SitePulse - Website Health Monitor")
        self.root.geometry("1100x750")
        
        # Initialize services
        self.website_service = WebsiteService(db_manager)
        self.health_checker = HealthChecker(timeout=10, check_ssl=True)
        self.report_service = ReportService(db_manager)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Create main layout
        self._create_layout()
        
        # Show dashboard by default
        self._show_dashboard()
    
    def _create_layout(self):
        """Create the main window layout."""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        sidebar = ttk.Frame(main_container, width=200, style="Sidebar.TFrame")
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        sidebar.pack_propagate(False)
        
        # Configure sidebar style
        self.style.configure("Sidebar.TFrame", background="#2c3e50")
        self.style.configure("Sidebar.TLabel", background="#2c3e50", foreground="white")
        self.style.configure("Nav.TButton", padding=10)
        
        # Title
        title_label = ttk.Label(
            sidebar, 
            text="SitePulse",
            font=("Arial", 18, "bold"),
            style="Sidebar.TLabel"
        )
        title_label.pack(pady=20)
        
        # Subtitle
        subtitle_label = ttk.Label(
            sidebar,
            text="Website Monitor",
            font=("Arial", 9),
            style="Sidebar.TLabel"
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Navigation buttons
        nav_buttons = [
            ("Dashboard", self._show_dashboard),
            ("Websites", self._show_websites),
            ("History", self._show_history),
            ("Reports", self._show_reports),
            ("Settings", self._show_settings),
        ]
        
        self.nav_buttons = []
        for text, command in nav_buttons:
            btn = ttk.Button(
                sidebar,
                text=text,
                command=command,
                width=18,
                style="Nav.TButton"
            )
            btn.pack(pady=5, padx=10)
            self.nav_buttons.append(btn)
        
        # Content area
        self.content_frame = ttk.Frame(main_container)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Store view references
        self.current_view = None
        self.dashboard_view = None
        self.websites_view = None
        self.history_view = None
        self.reports_view = None
    
    def _clear_content(self):
        """Clear the content area."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def _show_dashboard(self):
        """Show the dashboard view."""
        self._clear_content()
        
        # Always create a new view since we cleared the content
        self.dashboard_view = DashboardView(
            self.content_frame,
            self.website_service,
            self.health_checker
        )
    
    def _show_websites(self):
        """Show the websites management view."""
        self._clear_content()
        
        # Always create a new view since we cleared the content
        self.websites_view = WebsitesView(
            self.content_frame,
            self.website_service,
            self.health_checker
        )
    
    def _show_history(self):
        """Show the monitoring history view."""
        self._clear_content()
        
        # Always create a new view since we cleared the content
        self.history_view = HistoryView(
            self.content_frame,
            self.website_service
        )
    
    def _show_reports(self):
        """Show the reports view."""
        self._clear_content()
        
        # Always create a new view since we cleared the content
        self.reports_view = ReportsView(
            self.content_frame,
            self.website_service,
            self.report_service
        )
    
    def _show_settings(self):
        """Show the settings view."""
        self._clear_content()
        
        title = ttk.Label(
            self.content_frame,
            text="Settings",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=20)
        
        info = ttk.Label(
            self.content_frame,
            text="Application settings coming soon...",
            font=("Arial", 12)
        )
        info.pack(pady=40)
    
    def run(self):
        """Start the application main loop."""
        self.root.mainloop()
    
    def cleanup(self):
        """Cleanup resources before closing."""
        if self.health_checker:
            self.health_checker.close()
