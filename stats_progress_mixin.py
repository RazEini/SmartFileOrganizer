"""
StatsProgressMixin: updates the stat cards and the progress bar/label.
"""


class StatsProgressMixin:

    def _update_stats(self, total, moved, dup):

        self.total_files = total
        self.moved_files = moved
        self.duplicate_files = dup

        self.stats_total.config(text=str(total))
        self.stats_moved.config(text=str(moved))
        self.stats_duplicates.config(text=str(dup))

    def _update_progress(self, pct):

        self.progress_value.set(pct)
        self.progress_percent.config(text=f"{pct}%")
        self.status_label.config(text=f"Organizing files... {pct}%")

    def _finish_sort(self):

        self.progress_value.set(100)
        self.progress_percent.config(text="100%")

        self.sort_btn.config(state="normal")

        self.status_label.config(text="Organization completed successfully ✓")
        self.stats_status.config(text="DONE")

        self.root.after(1200, lambda: self.progress_value.set(0))
        self.root.after(1200, lambda: self.progress_percent.config(text="0%"))

        self.refresh_preview()
