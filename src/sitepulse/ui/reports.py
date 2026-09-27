"""
Reports view for SitePulse.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, timedelta

from ..services import WebsiteService, ReportService, ExportService


class ReportsView:
    """Reports view showing statistics and export options."""
    
    def __init__(self, parent, website_service: WebsiteService, report_service: ReportService):
        """
        Initialize the reports view.
        
        Args:
            parent: The parent frame
            website_service: The website service instance
            report_service: The report service instance
        """
        self.parent = parent
        self.website_service = website_service
        self.report_service = report_service
        
        self._create_widgets()
        self.refresh()
    
    def _create_widgets(self):
        """Create widgets for the reports view."""
        # Title
        title = ttk.Label(
            self.parent,
            text="Health Reports",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=(0, 20))
        
        # Filter frame
        filter_frame = ttk.LabelFrame(self.parent, text="Report Filters", padding=10)
        filter_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(filter_frame, text="Website:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.website_var = tk.StringVar(value="All Websites")
        self.website_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.website_var,
            state="readonly",
            width=30
        )
        self.website_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(filter_frame, text="Period:").grid(row=0, column=2, padx=(20, 5), pady=5, sticky=tk.W)
        
        self.period_var = tk.StringVar(value="Last 30 Days")
        period_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.period_var,
            state="readonly",
            width=20,
            values=["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"]
        )
        period_combo.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        ttk.Button(
            filter_frame,
            text="Generate Report",
            command=self.refresh
        ).grid(row=0, column=4, padx=20, pady=5)
        
        ttk.Button(
            filter_frame,
            text="Reload",
            command=self._reload_with_confirmation
        ).grid(row=0, column=5, padx=5, pady=5)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(self.parent, text="Statistics", padding=10)
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Create statistics grid
        self.stats_labels = {}
        stats = [
            ("Total Checks", "total_checks"),
            ("Successful Checks", "successful_checks"),
            ("Success Rate", "success_rate"),
            ("HTTP Errors", "http_errors"),
            ("Connection Failures", "connection_failures"),
            ("SSL Errors", "ssl_errors"),
            ("Timeouts", "timeouts"),
            ("DNS Failures", "dns_failures"),
            ("Average Response Time", "average_response_time"),
            ("Min Response Time", "min_response_time"),
            ("Max Response Time", "max_response_time"),
        ]
        
        for i, (label, key) in enumerate(stats):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(
                stats_frame,
                text=f"{label}:",
                font=("Arial", 10, "bold")
            ).grid(row=row, column=col, padx=10, pady=5, sticky=tk.W)
            
            value_label = ttk.Label(
                stats_frame,
                text="0",
                font=("Arial", 10)
            )
            value_label.grid(row=row, column=col+1, padx=10, pady=5, sticky=tk.W)
            self.stats_labels[key] = value_label
        
        # Export frame
        export_frame = ttk.LabelFrame(self.parent, text="Export Data", padding=10)
        export_frame.pack(fill=tk.X)
        
        ttk.Button(
            export_frame,
            text="📥 Download Current Report (CSV)",
            command=self._export_current_report
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            export_frame,
            text="Export Complete History to CSV",
            command=self._export_history
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            export_frame,
            text="Export Websites to CSV",
            command=self._export_websites
        ).pack(side=tk.LEFT, padx=5)
    
    def refresh(self):
        """Refresh the report data."""
        # Update website filter
        websites = self.website_service.get_all_websites()
        website_names = ["All Websites"] + [w.name for w in websites]
        self.website_combo['values'] = website_names
        
        # Get selected website ID
        selected_name = self.website_var.get()
        website_id = None
        if selected_name != "All Websites":
            for w in websites:
                if w.name == selected_name:
                    website_id = w.id
                    break
        
        # Calculate date range
        period = self.period_var.get()
        end_date = datetime.now()
        start_date = None
        
        if period == "Last 7 Days":
            start_date = end_date - timedelta(days=7)
        elif period == "Last 30 Days":
            start_date = end_date - timedelta(days=30)
        elif period == "Last 90 Days":
            start_date = end_date - timedelta(days=90)
        
        # Generate report
        report = self.report_service.generate_summary_report(
            website_id=website_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Update statistics
        self.stats_labels['total_checks'].config(text=str(report['total_checks']))
        self.stats_labels['successful_checks'].config(text=str(report['successful_checks']))
        self.stats_labels['success_rate'].config(text=f"{report['success_rate']}%")
        self.stats_labels['http_errors'].config(text=str(report['http_errors']))
        self.stats_labels['connection_failures'].config(text=str(report['connection_failures']))
        self.stats_labels['ssl_errors'].config(text=str(report['ssl_errors']))
        self.stats_labels['timeouts'].config(text=str(report['timeouts']))
        self.stats_labels['dns_failures'].config(text=str(report['dns_failures']))
        self.stats_labels['average_response_time'].config(text=f"{report['average_response_time']} ms")
        self.stats_labels['min_response_time'].config(text=f"{report['min_response_time']} ms")
        self.stats_labels['max_response_time'].config(text=f"{report['max_response_time']} ms")
    
    def _reload_with_confirmation(self):
        """Show confirmation dialog before reloading."""
        if self.stats_labels['total_checks'].cget('text') != '0':
            # There's data to potentially lose
            result = messagebox.askyesnocancel(
                "Reload Report",
                "Would you like to download the current report before reloading?\n\n"
                "• Click 'Yes' to download the report first\n"
                "• Click 'No' to reload without downloading\n"
                "• Click 'Cancel' to keep the current report",
                icon='question'
            )
            
            if result is None:  # Cancel
                return
            elif result:  # Yes - download first
                self._export_current_report()
                # After export, ask if they still want to reload
                confirm_reload = messagebox.askyesno(
                    "Reload Report",
                    "Report downloaded successfully!\n\nDo you want to reload now?",
                    icon='question'
                )
                if confirm_reload:
                    self._reset_report()
            else:  # No - reload directly
                self._reset_report()
        else:
            # No data, just reload
            self._reset_report()
    
    def _reset_report(self):
        """Reset the report to initial state."""
        # Reset filters to defaults
        self.website_var.set("All Websites")
        self.period_var.set("Last 30 Days")
        
        # Reset all statistics to zero
        self.stats_labels['total_checks'].config(text="0")
        self.stats_labels['successful_checks'].config(text="0")
        self.stats_labels['success_rate'].config(text="0.0%")
        self.stats_labels['http_errors'].config(text="0")
        self.stats_labels['connection_failures'].config(text="0")
        self.stats_labels['ssl_errors'].config(text="0")
        self.stats_labels['timeouts'].config(text="0")
        self.stats_labels['dns_failures'].config(text="0")
        self.stats_labels['average_response_time'].config(text="0 ms")
        self.stats_labels['min_response_time'].config(text="0 ms")
        self.stats_labels['max_response_time'].config(text="0 ms")
        
        messagebox.showinfo(
            "Report Reset",
            "Report has been reset to default state.\n\n"
            "Click 'Generate Report' to create a new report."
        )
    
    def _export_current_report(self):
        """Export the current filtered report to CSV."""
        # Get current filters
        selected_name = self.website_var.get()
        website_id = None
        
        websites = self.website_service.get_all_websites()
        
        if selected_name != "All Websites":
            for w in websites:
                if w.name == selected_name:
                    website_id = w.id
                    break
        
        # Calculate date range based on current period
        period = self.period_var.get()
        end_date = datetime.now()
        start_date = None
        
        if period == "Last 7 Days":
            start_date = end_date - timedelta(days=7)
        elif period == "Last 30 Days":
            start_date = end_date - timedelta(days=30)
        elif period == "Last 90 Days":
            start_date = end_date - timedelta(days=90)
        
        # Get filtered history
        history = self.website_service.get_check_history(
            website_id=website_id,
            start_date=start_date,
            end_date=end_date
        )
        
        if not history:
            messagebox.showinfo("No Data", "No check history in the current report to export")
            return
        
        # Generate filename with timestamp and filters
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        website_part = selected_name.replace(" ", "_") if selected_name != "All Websites" else "All"
        period_part = period.replace(" ", "_")
        suggested_name = f"SitePulse_Report_{website_part}_{period_part}_{timestamp}.csv"
        
        # Ask for file location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Download Current Report",
            initialfile=suggested_name
        )
        
        if not file_path:
            return
        
        # Export
        success = ExportService.export_check_history(history, websites, file_path)
        
        if success:
            messagebox.showinfo(
                "Success", 
                f"Current report downloaded successfully!\n\n"
                f"Records exported: {len(history)}\n"
                f"Period: {period}\n"
                f"Website: {selected_name}\n\n"
                f"File: {file_path}"
            )
        else:
            messagebox.showerror("Error", "Failed to download current report")
    
    def _export_history(self):
        """Export check history to CSV."""
        # Ask for file location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Check History"
        )
        
        if not file_path:
            return
        
        # Get data
        history = self.website_service.get_check_history()
        websites = self.website_service.get_all_websites()
        
        if not history:
            messagebox.showinfo("No Data", "No check history to export")
            return
        
        # Export
        success = ExportService.export_check_history(history, websites, file_path)
        
        if success:
            messagebox.showinfo("Success", f"Check history exported to:\n{file_path}")
        else:
            messagebox.showerror("Error", "Failed to export check history")
    
    def _export_websites(self):
        """Export websites list to CSV."""
        # Ask for file location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Websites"
        )
        
        if not file_path:
            return
        
        # Get data
        websites = self.website_service.get_all_websites()
        
        if not websites:
            messagebox.showinfo("No Data", "No websites to export")
            return
        
        # Export
        success = ExportService.export_websites(websites, file_path)
        
        if success:
            messagebox.showinfo("Success", f"Websites exported to:\n{file_path}")
        else:
            messagebox.showerror("Error", "Failed to export websites")
