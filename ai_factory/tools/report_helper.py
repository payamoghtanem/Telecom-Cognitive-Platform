import os
from typing import List

class ProjectStatusReporter:
    """
    A deterministic file utility enabling AI agents to programmatically update 
    task matrices and log architecture bottlenecks within project_status.md.
    """
    def __init__(self, report_path: str = "ai_factory/shared_memory/project_status.md"):
        self.report_path = report_path

    def update_task_status(self, task_id: str, new_status: str, note: str = "") -> None:
        """Reads the report markdown, identifies the task row, and alters state parameters."""
        if not os.path.exists(self.report_path):
            return
            
        with open(self.report_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        updated_lines: List[str] = []
        for line in lines:
            if task_id in line and "|" in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 6:
                    parts[5] = f"**{new_status}**" if "🛑" in new_status or "⏳" in new_status else new_status
                    if note:
                        parts[6] = note
                    line = " | ".join(parts) + "\n"
            updated_lines.append(line)

        with open(self.report_path, "w", encoding="utf-8") as f:
            f.writelines(updated_lines)

if __name__ == "__main__":
    reporter = ProjectStatusReporter("ai_factory/shared_memory/project_status.md")
    reporter.update_task_status("TS-000", "✅ DONE", "Workspace scaffolding successfully initialized on autopilot.")
    print("✅ Project report status updated to DONE successfully!")