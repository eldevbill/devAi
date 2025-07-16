import argparse
import os
import json
import subprocess
import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("orchestrator.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Configuration (can be loaded from a file later)
CONFIG = {}

def load_config(config_path="config.json"):
    global CONFIG
    try:
        with open(config_path, 'r') as f:
            CONFIG = json.load(f)
        logger.info(f"Configuration loaded from {config_path}")
    except FileNotFoundError:
        logger.warning(f"Config file {config_path} not found. Using default empty config.")
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from {config_path}. Using default empty config.")

def check_agent_availability(agent_name):
    import shutil
    if shutil.which(agent_name):
        return True
    else:
        logger.warning(f"Agent '{agent_name}' not found in system PATH. Please install it.")
        return False

async def run_agent(agent_name, task, project_path):
    """
    Runs an AI agent asynchronously.
    """
    logger.info(f"Starting agent: {agent_name} for task: '{task}' in project: {project_path}")
    command = ""
    if agent_name == "smol-developer":
        command = f"smol-developer --task \"{task}\" --path \"{project_path}\""
    elif agent_name == "aider":
        command = f"aider --message \"{task}\" --dir \"{project_path}\""
    elif agent_name == "shell-gpt":
        command = f"shell-gpt --prompt \"{task}\" --output-dir \"{project_path}\""
    elif agent_name == "quantum-agent": # Conceptual Quantum Agent
        logger.info(f"Simulating quantum agent execution for task: '{task}'")
        # In a real scenario, this would involve calling a quantum computing SDK or API
        # For now, we'll just simulate a delay and success/failure
        await asyncio.sleep(5) # Simulate work
        if "fail" in task.lower():
            logger.warning(f"Quantum agent simulated failure for task: '{task}'")
            return False
        else:
            logger.info(f"Quantum agent simulated success for task: '{task}'")
            return True
    elif agent_name == "xuabgicos-agent": # Conceptual Xuabgicos Agent
        logger.info(f"Simulating xuabgicos agent execution for task: '{task}'")
        # This agent will interact with the shared context
        context_path = os.path.join(project_path, "memory", "context.json")
        try:
            with open(context_path, 'r+') as f:
                context = json.load(f)
                context['xuabgicos_observations'] = f"Symbiotic link established for task: {task}"
                f.seek(0)
                json.dump(context, f, indent=4)
        except (FileNotFoundError, json.JSONDecodeError):
            with open(context_path, 'w') as f:
                json.dump({'xuabgicos_observations': f"Symbiotic link established for task: {task}"}, f, indent=4)
        await asyncio.sleep(3) # Simulate work
        logger.info(f"Xuabgicos agent simulated success for task: '{task}'")
        return True
    elif agent_name == "review-agent": # Conceptual Review Agent
        logger.info(f"Simulating review agent execution for task: '{task}'")
        # This agent will read the shared context and provide a summary
        context_path = os.path.join(project_path, "memory", "context.json")
        summary = "No context to review."
        try:
            with open(context_path, 'r') as f:
                context = json.load(f)
                summary = f"Review of shared context: {json.dumps(context, indent=2)}"
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        logger.info(summary)
        await asyncio.sleep(2) # Simulate work
        logger.info(f"Review agent simulated success for task: '{task}'")
        return True
    else:
        logger.error(f"Unknown agent: {agent_name}")
        return False

    try:
        logger.info(f"Executing command for {agent_name}: {command}")
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=project_path
        )

        timeout = CONFIG.get("timeout_seconds", 600) # Default to 600 seconds if not in config
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(f"Agent {agent_name} timed out after {timeout} seconds. Terminating process.")
            process.kill()
            stdout, stderr = await process.communicate() # Get any output before termination
            log_file_name = f"{agent_name}_{datetime.now().strftime('%Y%m%d-%H%M%S')}_timeout.log"
            log_file_path = os.path.join(project_path, "logs", log_file_name)

            with open(log_file_path, "w") as f:
                f.write(f"--- Agent: {agent_name} (TIMED OUT) ---\n")
                f.write(f"--- Task: {task} ---\n")
                f.write(f"--- Command: {command} ---\n")
                f.write(f"--- Timeout: {timeout} seconds ---\n")
                f.write(f"--- Exit Code: {process.returncode} (likely -9 for killed process) ---\n")
                if stdout:
                    f.write(f"--- STDOUT (before timeout) ---\n{stdout.decode()}\n")
                if stderr:
                    f.write(f"--- STDERR (before timeout) ---\n{stderr.decode()}\n")
            logger.info(f"Agent {agent_name} logs (including timeout info) saved to {log_file_path}")
            return False # Agent failed due to timeout

        log_file_name = f"{agent_name}_{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
        log_file_path = os.path.join(project_path, "logs", log_file_name)

        with open(log_file_path, "w") as f:
            f.write(f"--- Agent: {agent_name} ---\n")
            f.write(f"--- Task: {task} ---\n")
            f.write(f"--- Command: {command} ---\n")
            f.write(f"--- Exit Code: {process.returncode} ---\n")
            if stdout:
                f.write(f"--- STDOUT ---\n{stdout.decode()}\n")
            if stderr:
                f.write(f"--- STDERR ---\n{stderr.decode()}\n")

        logger.info(f"Agent {agent_name} finished with exit code {process.returncode}. Logs saved to {log_file_path}")

        if process.returncode != 0:
            logger.error(f"Agent {agent_name} failed. Check logs for details.")
            return False
        return True
    except Exception as e:
        logger.error(f"Error running agent {agent_name}: {e}")
        return False

def create_project_structure(project_path, project_type):
    """
    Creates the basic project directory structure and files based on project type.
    """
    logger.info(f"Creating project structure for type: {project_type} at {project_path}")
    try:
        os.makedirs(project_path, exist_ok=True)
    except OSError as e:
        logger.error(f"Error creating project directory {project_path}: {e}")
        return False

    # Default structure
    default_structure = ["src", "tests", "docs", "logs", "memory"]
    for folder in default_structure:
        try:
            os.makedirs(os.path.join(project_path, folder), exist_ok=True)
        except OSError as e:
            logger.error(f"Error creating default structure folder {folder} in {project_path}: {e}")
            return False

    # Specific sub-structures based on templates
    if project_type in CONFIG["project_templates"]:
        template = CONFIG["project_templates"][project_type]
        src_path = os.path.join(project_path, "src")
        docs_path = os.path.join(project_path, "docs")

        file_to_subdir_map = template.get("file_to_subdir_map", {})

        for sub_folder in template["structure"]:
            try:
                os.makedirs(os.path.join(src_path, sub_folder), exist_ok=True)
            except OSError as e:
                logger.error(f"Error creating template sub-folder {sub_folder} in {src_path}: {e}")
                return False

        for file_name in template["files"]:
            target_subdir = file_to_subdir_map.get(file_name)
            if target_subdir:
                if file_name.endswith(".md") and target_subdir == "paradigms": # Special case for docs in docs folder
                    target_dir = os.path.join(src_path, target_subdir)
                elif file_name.endswith(".md"):
                    target_dir = docs_path
                else:
                    target_dir = os.path.join(src_path, target_subdir)
                try:
                    os.makedirs(target_dir, exist_ok=True)
                except OSError as e:
                    logger.error(f"Error creating target directory {target_dir} for {file_name}: {e}")
                    return False
                file_path = os.path.join(target_dir, file_name)
            else:
                # If no specific subdir is mapped, place in src/core as a fallback
                target_dir = os.path.join(src_path, "core")
                try:
                    os.makedirs(target_dir, exist_ok=True)
                except OSError as e:
                    logger.error(f"Error creating fallback directory {target_dir} for {file_name}: {e}")
                    return False
                file_path = os.path.join(target_dir, file_name)
                logger.warning(f"No specific subdirectory mapped for {file_name}. Placing in {target_dir}")

            try:
                with open(file_path, "w") as f:
                    file_extension = os.path.splitext(file_name)[1]
                    initial_content = CONFIG.get("initial_file_contents", {}).get(file_extension, CONFIG.get("initial_file_contents", {}).get("default", f"# Initial content for {file_name}\n"))
                    f.write(initial_content.format(file_name=file_name))
            except IOError as e:
                logger.error(f"Error writing file {file_path}: {e}")
                return False

    # Create README.md and requirements.txt
    try:
        with open(os.path.join(project_path, "README.md"), "w") as f:
            f.write(f"# {os.path.basename(project_path)} - Crypto AI Orchestrator Project\n\n")
            f.write("This project was generated by the Crypto AI Orchestrator.\n")

        with open(os.path.join(project_path, "requirements.txt"), "w") as f:
            f.write("smol-developer\n")
            f.write("aider-chat\n")
            f.write("shell-gpt\n")
    except IOError as e:
        logger.error(f"Error writing README.md or requirements.txt in {project_path}: {e}")
        return False

    logger.info(f"Project structure created successfully.")
    return True

async def main():
    load_config()

    # Ensure memory directory exists
    memory_dir = os.path.join(os.getcwd(), "memory")
    try:
        os.makedirs(memory_dir, exist_ok=True)
    except OSError as e:
        logger.error(f"Error creating memory directory {memory_dir}: {e}")
        return # Exit if memory directory cannot be created

    parser = argparse.ArgumentParser(description="Crypto AI Orchestrator - A multi-agent AI development system.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Orchestrate command
    orchestrate_parser = subparsers.add_parser("orchestrate", help="Orchestrate a new project.")
    orchestrate_parser.add_argument("--task", required=True, help="The development task to perform.")
    orchestrate_parser.add_argument("--project-type", default="revolution", help="Type of project (e.g., python, web, defi, quantum).")
    orchestrate_parser.add_argument("--agents", nargs="+", default=CONFIG.get("default_agents", ["smol-developer", "aider", "shell-gpt"]),
                                    help="List of AI agents to use (e.g., smol-developer aider shell-gpt).")
    orchestrate_parser.add_argument("--workspace", default=os.getcwd(),
                                    help="Base directory for the project workspace. Defaults to current working directory.")
    orchestrate_parser.add_argument("--project-path",
                                    help="Specific path for the new project. If not provided, a path will be generated.")

    # History command
    history_parser = subparsers.add_parser("history", help="Display orchestration history.")

    args = parser.parse_args()

    if args.command == "history":
        display_history(memory_dir)
        return
    
    if args.command == "orchestrate":
        try:
            # Existing orchestration logic starts here
            orchestration_record = {
                "timestamp_start": datetime.now().isoformat(),
                "task": args.task,
                "project_type": args.project_type,
                "agents_requested": args.agents,
                "project_path": None,
                "status": "failed", # Default to failed, update to success if all goes well
                "timestamp_end": None,
                "agent_results": {}
            }

            # Resolve project path
            if args.project_path:
                full_project_path = os.path.abspath(os.path.join(args.workspace, args.project_path))
            else:
                # Generate a project path based on task and timestamp
                task_slug = args.task.lower().replace(" ", "-").replace("/", "-")[:50]
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                project_name = f"orchestrated-project-{task_slug}-{timestamp}"
                full_project_path = os.path.abspath(os.path.join(args.workspace, project_name))

            orchestration_record["project_path"] = full_project_path

            logger.info(f"Starting Crypto AI Orchestration for task: '{args.task}'")
            logger.info(f"Project will be created at: {full_project_path}")

            # Create project structure
            if not create_project_structure(full_project_path, args.project_type):
                orchestration_record["status"] = "failed_structure_creation"
                logger.error(f"Project structure creation failed for {full_project_path}. Aborting orchestration.")
                return

            # Prepare agent tasks for asynchronous execution
            agent_tasks = []
            agents_to_run = []
            for agent in args.agents:
                if check_agent_availability(agent):
                    agent_tasks.append(run_agent(agent, args.task, full_project_path))
                    agents_to_run.append(agent)
                else:
                    logger.warning(f"Skipping agent {agent} due to unavailability.")
                    orchestration_record["agent_results"][agent] = {"status": "skipped", "reason": "not available"}

            # Run agents concurrently
            if agent_tasks:
                results = await asyncio.gather(*agent_tasks, return_exceptions=True)
                for i, agent in enumerate(agents_to_run):
                    if isinstance(results[i], Exception):
                        orchestration_record["agent_results"][agent] = {"status": "error", "details": str(results[i])}
                    else:
                        orchestration_record["agent_results"][agent] = {"status": "success" if results[i] else "failed"}

            # Determine overall status
            all_agents_succeeded = all(res.get("status") == "success" for res in orchestration_record["agent_results"].values())
            if all_agents_succeeded and agents_to_run:
                orchestration_record["status"] = "success"
            elif not agents_to_run:
                orchestration_record["status"] = "no_agents_run"

            orchestration_record["timestamp_end"] = datetime.now().isoformat()

            # Save orchestration record to memory
            record_filename = f"orchestration_record_{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
            record_filepath = os.path.join(memory_dir, record_filename)
            try:
                with open(record_filepath, "w") as f:
                    json.dump(orchestration_record, f, indent=4)
                logger.info(f"Orchestration record saved to: {record_filepath}")
            except IOError as e:
                logger.error(f"Error saving orchestration record to {record_filepath}: {e}")

            logger.info(f"Orchestration complete for task: '{args.task}'")
            logger.info(f"Check the generated project at: {full_project_path}")

        except Exception as e:
            logger.critical(f"An unhandled critical error occurred during orchestration: {e}", exc_info=True)
            # Attempt to save a minimal record of the critical failure
            if 'orchestration_record' in locals():
                orchestration_record["status"] = "critical_failure"
                orchestration_record["timestamp_end"] = datetime.now().isoformat()
                orchestration_record["error_details"] = str(e)
                record_filename = f"orchestration_record_critical_failure_{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
                record_filepath = os.path.join(memory_dir, record_filename)
                try:
                    with open(record_filepath, "w") as f:
                        json.dump(orchestration_record, f, indent=4)
                    logger.info(f"Critical failure record saved to: {record_filepath}")
                except IOError as save_e:
                    logger.error(f"Failed to save critical failure record: {save_e}")
            else:
                logger.error("Could not save orchestration record for critical failure as record object was not initialized.")

def display_history(memory_dir):
    logger.info(f"Displaying orchestration history from: {memory_dir}")
    records = []
    try:
        for filename in os.listdir(memory_dir):
            if filename.startswith("orchestration_record_") and filename.endswith(".json"):
                filepath = os.path.join(memory_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        record = json.load(f)
                        records.append(record)
                except json.JSONDecodeError as e:
                    logger.error(f"Error decoding JSON from history file {filename}: {e}")
                except IOError as e:
                    logger.error(f"Error reading history file {filename}: {e}")
    except OSError as e:
        logger.error(f"Error accessing memory directory {memory_dir}: {e}")
        logger.info(f"No orchestration history found.")
        return

    if not records:
        logger.info(f"No orchestration history found.")
        return

    # Sort records by timestamp (newest first)
    records.sort(key=lambda x: x.get("timestamp_start", ""), reverse=True)

    for i, record in enumerate(records):
        logger.info(f"\n--- Orchestration Record {i+1} ---")
        logger.info(f"  Task: {record.get("task", "N/A")}")
        logger.info(f"  Project Type: {record.get("project_type", "N/A")}")
        logger.info(f"  Project Path: {record.get("project_path", "N/A")}")
        logger.info(f"  Status: {record.get("status", "N/A").upper()}")
        logger.info(f"  Start Time: {record.get("timestamp_start", "N/A")}")
        logger.info(f"  End Time: {record.get("timestamp_end", "N/A")}")
        logger.info(f"  Agents Requested: {", ".join(record.get("agents_requested", []))}")
        agent_results = record.get("agent_results", {})
        if agent_results:
            logger.info("  Agent Results:")
            for agent, res in agent_results.items():
                status = res.get("status", "N/A")
                details = res.get("details", "")
                logger.info(f"    - {agent}: {status.upper()} {f"({details})" if details else ""}")

if __name__ == "__main__":
    asyncio.run(main())